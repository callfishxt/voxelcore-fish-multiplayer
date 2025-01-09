import socket
import threading
from server_time import ServerTime
from changes import ChangeManager as change_manager
from server_commands_handler import Commands_Handler as commands_handler


players = {}
mp_size = {}
blocks = {} 
changes = change_manager()


utsc = ["ep"]

def split_pack_by_bytes(pack, chunk_size):    
    chunks = []

    for i in range(0, len(pack), chunk_size):
        chunks.append(pack[i:i + chunk_size])
    
    return chunks

def load_changes_for_user(client_socket: socket.socket):
    for item in changes.to_list():
        #print("sync" + item)
        client_socket.send(f"{item};".encode('utf-8'))



def handle_client(client_socket, address):
    print(f"Connected: {address}")
    nickname = None
    is_sync = False
    if not is_sync: 
        load_changes_for_user(client_socket)
        is_sync = True


    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            
            messages = data.split(';')

            for message in messages:
                if message:
                    print("PACK: R " + message) 
                    command, *args = message.split()
                    
                    match command:
                        case "con":
                            if len(args) == 5:
                                nickname = args[0]
                                x, y, z = (args[1], args[2], args[3])
                                max_pack_size = args[4]
                                players[nickname] = client_socket
                                mp_size[nickname] = int(max_pack_size)
                                print(f"{nickname} connected.")

                        case "bp":
                            if len(args) == 5:
                                block_id, x, y, z, rot = args
                                place_block(block_id, int(x), int(y), int(z), int(rot), nickname)
                        case "bb":
                            if len(args) == 4:
                                block_id, x, y, z = args
                                break_block(block_id, int(x), int(y), int(z), nickname)
                        case "ep":
                            if len(args) == 4:
                                x, y, z, x_angle = args
                                entity_pos(nickname, x, y, z, x_angle)
                        case "rm":
                            if len(args) == 1:
                                id = args[0]
                                refresh_model(nickname, id)
                        case "chat":
                            if len(args) == 1:
                                message = args[0]
                                msg = f"chat {nickname} {message}"
                                broadcast(msg,nickname)

            
        except Exception as e:
            print(f"Error: {e}")
            break

    if nickname:
        try:
            del players[nickname]
        except:
            print("")
        broadcast(f"dcon {nickname}",nickname)
        #print(f"{nickname} disconnected.")

    client_socket.close()

def place_block(block_id, x, y, z, rot, player_nickname):
    broadcast(f"bp {block_id} {x} {y} {z} {rot}", exclude=player_nickname)
    #print(f"GET <{player_nickname}> block_place {block_id} {x} {y} {z} {rot}")

def break_block(block_id, x, y, z, player_nickname):
    broadcast(f"bb {block_id} {x} {y} {z}",exclude=player_nickname)
    #print(f"GET <{player_nickname}> block_break {block_id} {x} {y} {z}")

def entity_pos(player_nickname,x,y,z,x_angle):
    broadcast(f"ep {player_nickname} {x} {y} {z} {x_angle}",player_nickname)
    #print(f"GET <{player_nickname}> entity_pos  {x} {y} {z} {x_angle}")

def refresh_model(player_nickname,id):
    broadcast(f"rm {player_nickname} {id}", exclude=player_nickname)
    #print(f"rm {player_nickname} {id}", exclude=player_nickname)
    #print(f"GET <{player_nickname}> refresh_model {player_nickname} {id}")

# def entity_body_rot(player_nickname,x):
#     broadcast(f"entity_body_rot {player_nickname} {x}",player_nickname)
#     print(f"GET <{player_nickname}> entity_body_rot  {x}")

def set_time(seconds):
    broadcast(f"st {seconds}")
    #print(f"POST <EVERYONE> set_time {seconds}")

def broadcast(message:str,exclude=""):
    if message.split()[0] not in utsc:
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

def start_server(host='0.0.0.0', port=12346):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server started on {host}:{port}")

    while True:

        client_socket, address = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, address))
        client_handler.start()






if __name__ == "__main__":
    server_time = ServerTime(set_time)  
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    time_thread = threading.Thread(target=server_time.uptime())
    time_thread.start()
    _commands_handler = commands_handler(changes)
    _commands_handler.start()
    

