local socket
local connected = false
local _entities = {}
local _nickname
local last_position = {x = 0, y = 0, z = 0}
local last_update_time = 0
local update_interval = 0.05
local movement_threshold = 0.01

function connect_to_server(ip,port,nickname)
    network.tcp_connect(ip, port, function(s)
        socket = s
        print("Connected to server!")
        x,y,z = player.get_pos()
        _nickname = nickname
        socket:send("connect " .. nickname.." "..x.." "..y.." "..z)
		connected = true
    end)
end



function receive_data()
	local data = utf8.tostring(socket:recv(1024))
	if data and type(data) == "string" then
		if data ~= "" then
			print("Received Data: " .. data) 
			process_server_data(data)
		end
	end
    
end

function process_server_data(data)
    local messages = mysplit(data, "\n")
    for _, message in ipairs(messages) do
        local command, args = message:match("^(%S+)%s*(.*)$")
        if command == "block_place" then
            local block_id, x, y, z, rot = args:match("(%S+) (%S+) (%S+) (%S+) (%S+)")
			block.set(x,y,z,block_id)
			block.set_rotation(x,y,z,rot)
            print(string.format("GET block_place  %s  %d, %d, %d, %d", block_id, x, y, z, rot))
        elseif command == "block_break" then
            local block_id, x, y, z = args:match("(%S+) (%S+) (%S+) (%S+)")	
            print(string.format("GET block_break  %s  %d, %d, %d", block_id, x, y, z))
			block.set(x,y,z,0)
        elseif command == "entity_pos" then
            local nickname, x, y, z = args:match("(%S+) (%S+) (%S+) (%S+)")	
            print(nickname.._nickname)
            if _entities[nickname] ~= nil and _entities[nickname] ~= _nickname then
                print("entity_pos "..nickname.." "..x.." "..y.." "..z)
                local tsf = _entities[nickname].transform 
                tsf:set_pos({x,y,z})
            elseif _entities[nickname] == nil then
                _entities[nickname] = entities.spawn("fish_multiplayer:player", {x,y,z})
            end
        elseif command == "disconnect" then
            local nickname = args:match("(%S+)")	
            if _entities[nickname] ~= nil then
                _entities[nickname]:despawn()
                print("despawn "..nickname)
                _entities[nickname] = nil
            end
        end
    end
end

function on_block_placed(block_id, x, y, z)
	local rot = block.get_rotation(x,y,z)
	print("POST block_place "..block_id.." "..x.." "..y.." "..z..""..rot)
	place_block(block_id,x,y,z,rot)
end

function on_block_broken(block_id, x, y, z)
	print("POST block_break "..block_id.." "..x.." "..y.." "..z)
	break_block(block_id,x,y,z)
end


function place_block(block_id, x, y, z,rot)
    if socket and socket:is_connected() then
        local message = string.format("block_place %s %d %d %d %d", block_id, x, y, z, rot)
        socket:send(message)
    end
end

function break_block(block_id, x, y, z)
    if socket and socket:is_connected() then
        local message = string.format("block_break %s %d %d %d",  block_id, x, y, z)
        socket:send(message)
    end
end

function mysplit(inputstr, sep)
    if sep == nil then
        sep = "%s"
    end
    local t = {}
    for str in string.gmatch(inputstr, "([^"..sep.."]+)") do
        table.insert(t, str)
    end
    return t
end


function on_world_open() 
    console.add_command(
        "connect ip:str='127.0.0.1' port:num=12345 nickname:str='Jim'",
        "connect to server", 
        function (args, kwargs) 
            connect_to_server(unpack(args))
            return "try connect"
        end
    )
end
function on_world_tick()

    if connected == true then

        receive_data()


        local x, y, z = player.get_pos()
        local current_time = os.clock()


        if (math.abs(x - last_position.x) > movement_threshold or
            math.abs(y - last_position.y) > movement_threshold or
            math.abs(z - last_position.z) > movement_threshold) and
            (current_time - last_update_time > update_interval) then
            socket:send("entity_pos " .. x .. " " .. y .. " " .. z)
            print("POST entity_pos " .. x .. " " .. y .. " " .. z)
            last_position = {x = x, y = y, z = z}
            last_update_time = current_time
        end
    end
end

function on_world_quit()
    if socket then
        socket:close()
    end
    
    for nick, ent in pairs(_entities) do
        if ent then
            ent:despawn() 
            print("Despawned entity: " .. nick)
        end
    end
    
end
