import socket
import threading
import json
from server_time import ServerTime
from changes import ChangeManager as change_manager
from server_commands_handler import Commands_Handler as commands_handler
from server_config import Config

players = {}
mp_size = {}

config = Config()
config.load()



changes = change_manager()

def set_time(seconds):
    broadcast(f"st {seconds}")

server_time = ServerTime(set_time,changes,config)  
server_commands_handler = commands_handler(changes,server_time)

def split_pack_by_bytes(pack, chunk_size):    
    chunks = []

    for i in range(0, len(pack), chunk_size):
        chunks.append(pack[i:i + chunk_size])
    
    return chunks

def load_changes_for_user(client_socket: socket.socket):
    for item in changes.to_list():
        client_socket.send(f"{item}".encode('utf-8'))

def handle_client(client_socket, address):
    print(f"Connected: {address}")
    nickname = None
    is_sync = False
    if not is_sync: 
        load_changes_for_user(client_socket)
        is_sync = True

    while True:
        try:
            data = client_socket.recv(4096).decode('utf-8')

            

            if not data:
                break
            
            if data.startswith('GET'):
                json_data = {
                    "online": len(players),
                    "generator": config.world_generator,
                    "seed": int(config.world_seed),
                    "allowed_content_packs": config.allowed_content_packs,
                    "optional_content_packs": config.optional_content_packs,
                    "status": "success"
                }
                json_response = json.dumps(json_data, ensure_ascii=True)

                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/json; charset=utf-8\r\n'
                response += 'Content-Length: {}\r\n'.format(len(json_response))
                response += '\r\n'
                response += json_response

                client_socket.sendall(response.encode('utf-8'))
                continue

            messages = data.split(';')

            for message in messages:
                if message:
                    print("PACK: R " + message) 
                    command, *args = message.split()
                    
                    match command:
                        case "con":
                            if len(args) == 8:
                                unacceptable = False
                                nickname = args[0]
                                x, y, z = (args[1], args[2], args[3])
                                max_pack_size = args[4]
                                content_packs = str(args[5]).split("/")
                                seed,generator = (args[6],args[7])
                                players[nickname] = client_socket
                                mp_size[nickname] = int(max_pack_size)
                                for content_pack in content_packs:
                                    if content_pack not in config.allowed_content_packs and content_pack not in config.optional_content_packs and unacceptable == False:
                                        client_socket.close()
                                        players.pop(nickname)
                                        broadcast(f"dcon {nickname}",nickname)
                                        unacceptable = True
                                        break
                                
                                if str(seed) != config.world_seed or generator != config.world_generator and unacceptable == False:
                                    client_socket.close()
                                    players.pop(nickname)
                                    unacceptable = True 
                                    broadcast(f"dcon {nickname}",nickname)
                                    
                                    

                                print(f"{nickname} connected.")

                        case "bp":
                            if len(args) == 5:
                                block_id, x, y, z, rot = args
                                broadcast(f"bp {block_id} {x} {y} {z} {rot}", exclude=nickname)
                        case "bb":
                            if len(args) == 4:
                                block_id, x, y, z = args
                                broadcast(f"bb {block_id} {x} {y} {z}",exclude=nickname)
                        case "bsr":
                            if len(args) == 4:
                                x, y, z, rot = args
                                broadcast(f"bsr {x} {y} {z} {rot}",exclude=nickname)
                        case "ep":
                            if len(args) == 5:
                                x, y, z, x_angle, y_angle = args
                                broadcast(f"ep {nickname} {x} {y} {z} {x_angle} {y_angle}",nickname)
                        case "rm":
                            if len(args) == 1:
                                id = args[0]
                                broadcast(f"rm {nickname} {id}", exclude=nickname)
                        case "chat":
                            if len(args) == 1:
                                message = args[0]
                                msg = f"chat {nickname} {message}"
                                broadcast(msg,nickname)
                        case "sc":
                            if address[0] in config.ops:
                                _dat = str(args[0]).replace("/"," ").replace('"',"").split(" ")
                                command, *_args = _dat
                                server_commands_handler.execute(command,_args)
                        case "pop":
                            msg = f"pop {len(players)}"
                            max_pack_size = mp_size[nickname]
                            _message = msg + ";"
                            size = len(_message.encode('utf-8'))
                            if size <= max_pack_size:
                                players[nickname].send(_message.encode('utf-8'))
                            else:
                                pack_arr = split_pack_by_bytes(_message.encode('utf-8'),max_pack_size)
                                for pack in pack_arr:
                                    players[nickname].send(pack)
        except Exception as e:
            print(f"Error: {e}")
            break

    if nickname in players:
        try:
            players.pop(nickname)
        except:
            print("Error while deleting player data")
        broadcast(f"dcon {nickname}",nickname)

    client_socket.close()

def broadcast(message:str,exclude=""):
    if message.split()[0] in config.saving_commands:
        changes.add_change(message)
    for player in players:
        try:
            if player != exclude:
                max_pack_size = mp_size[player]
                _message = message + ";"
                size = len(_message.encode('utf-8'))
                if size <= max_pack_size:
                    players[player].send(_message.encode('utf-8'))
                else:
                    pack_arr = split_pack_by_bytes(_message.encode('utf-8'),max_pack_size)
                    for pack in pack_arr:
                        players[player].send(pack)

        except Exception as e:
            print(f"Message send error: {e}")

def start_server(host=config.address, port=config.port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server started on {host}:{port}")
    while True:
        client_socket, address = server.accept()
        
        if config.white_list == True:
            if address[0] in config.allowed_ips:
                print(address[0]+" in whitelist. Connecting...")
                client_handler = threading.Thread(target=handle_client, args=(client_socket, address))
                client_handler.start()
            else:
                print(address[0]+" is not in whitelist!")
                client_socket.close()
        elif config.white_list == False:
            client_handler = threading.Thread(target=handle_client, args=(client_socket, address))
            client_handler.start()

if __name__ == "__main__":
    
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    time_thread = threading.Thread(target=server_time.uptime())
    time_thread.start()