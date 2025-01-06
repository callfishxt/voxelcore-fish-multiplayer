import socket
import threading


from changes import ChangeManager as change_manager
from server_commands_handler import Commands_Handler as commands_handler
players = {}
blocks = {} 
changes = change_manager()
utsc = ["entity_pos","entity_rot"]
def load_changes_for_user(client_socket: socket.socket):
    for item in changes.to_list():
        print("sync" + item)
        client_socket.send(f"{item}\n".encode('utf-8'))



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
            
            command, *args = data.split()
            if command == "connect":
                nickname = args[0]
                x,y,z = (args[1],args[2],args[3])
                players[nickname] = client_socket
                
                print(f"{nickname} connected.")
                
            elif command == "block_place":
                block_id, x, y, z, rot = args
                place_block(block_id, int(x), int(y), int(z), int(rot), nickname)
            elif command == "block_break":
                block_id, x, y, z = args
                break_block(block_id, int(x), int(y), int(z), nickname)
            elif command == "entity_pos":
                x,y,z = args
                entity_pos(nickname,x,y,z)
            else:
                print(f"Unknown command {data} from {nickname}")
            
        except Exception as e:
            print(f"Error: {e}")
            break

    if nickname:
        del players[nickname]
        broadcast(f"disconnect {nickname}",nickname)
        print(f"{nickname} disconnected.")

    client_socket.close()

def place_block(block_id, x, y, z, rot, player_nickname):
    broadcast(f"block_place {block_id} {x} {y} {z} {rot}", exclude=player_nickname)
    print(f"GET <{player_nickname}> block_place {block_id} {x} {y} {z} {rot}")

def break_block(block_id, x, y, z, player_nickname):
    broadcast(f"block_break {block_id} {x} {y} {z}",exclude=player_nickname)
    print(f"GET <{player_nickname}> block_break {block_id} {x} {y} {z}")

def entity_pos(player_nickname,x,y,z):
    broadcast(f"entity_pos {player_nickname} {x} {y} {z}",player_nickname)
    print(f"GET <{player_nickname}> entity_pos  {x} {y} {z}")


def broadcast(message:str,exclude=""):
    if message.split()[0] not in utsc:
        changes.add_change(message)
    for player in players:
        try:
            if player != exclude:
                players[player].send(message.encode('utf-8'))
        except Exception as e:
            print(f"Message send error: {e}")

def start_server(host='127.0.0.1', port=12346):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server started on {host}:{port}")

    while True:
        client_socket, address = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, address))
        client_handler.start()



if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    _commands_handler = commands_handler(changes)
    _commands_handler.start()
    