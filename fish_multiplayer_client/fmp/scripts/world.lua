require "globals"

local socket
local connected = false
local _entities = {}
local _nickname

local last_position = {x = 0, y = 0, z = 0, x_angle=0}
local last_update_time = 0
local update_interval = 0.1
local movement_threshold = 0.01
local max_packet_size = 2048
local last_itemid = 0

function connect_to_server(ip,port,nickname)
    network.tcp_connect(ip, port, function(s)
        socket = s
        print("Connected to server!")
        x,y,z = player.get_pos()
        _nickname = nickname
        socket:send("con " .. nickname.." "..x.." "..y.." "..z.." "..max_packet_size..";")
		connected = true
    end)
end



function receive_data()
	local data = utf8.tostring(socket:recv(1024))
	if data and type(data) == "string" then
		if data ~= "" then
			print("R: " .. data) 
			process_server_data(data)
		end
	end
    
end

function process_server_data(data)
    local messages = mysplit(data, ";")
    for _, message in ipairs(messages) do
        local command, args = message:match("^(%S+)%s*(.*)$")
        if command and command ~= "" then
            if command == "bp" then
                local block_id, x, y, z, rot = args:match("(%S+) (%S+) (%S+) (%S+) (%S+)")
                if block_id ~= nil and x ~= nil and y ~= nil and z ~= nil and rot ~= nil then
                    print("GET bp "..block_id.." "..x.." "..y.." "..z.." "..rot)
                    block.set(x,y,z,block_id)
                    block.set_rotation(x,y,z,rot)
                else
                    print("ERROR packet dropped")
                end 
            elseif command == "bb" then
                local block_id, x, y, z = args:match("(%S+) (%S+) (%S+) (%S+)")	
                if block_id ~= nil and x ~= nil and y ~= nil and z ~= nil then
                    print("GET bb "..block_id.." "..x.." "..y.." "..z)
                    block.set(x,y,z,0)
                else
                    print("ERROR packet dropped")
                end
            elseif command == "ep" then
                local nickname, x, y, z, x_angle = args:match("(%S+) (%S+) (%S+) (%S+) (%S+)")	
                print(nickname.._nickname)
                
                if _entities[nickname] ~= null and _entities[nickname] ~= _nickname and fmp.playerdat[ent_uid] ~= nil then
                    print("ep "..nickname.." "..x.." "..y.." "..z)
                    print("ebr "..nickname.." "..x_angle)    
                    ent_uid =  _entities[nickname]:get_uid()
                    print(ent_uid)
                    fmp.playerdat[ent_uid].position = {tonumber(x), tonumber(y), tonumber(z)}
                    
                    
                    fmp.playerdat[ent_uid].body_rotation = tonumber(x_angle)

                elseif _entities[nickname] == nil then
                    _entities[nickname] = entities.spawn("fmp:player", {x,y,z})
                    ent_uid =  _entities[nickname]:get_uid()
                    if fmp.playerdat[ent_uid] == nil then fmp.playerdat[ent_uid] = {} end
                    fmp.playerdat[ent_uid].text_3d = gfx.text3d.show({tonumber(x), tonumber(y)+1.25, tonumber(z)},nickname,{["display"]="xy_free_billboard",["scale"]=0.015,["render_scale"]=128})
                    fmp.playerdat[ent_uid].position = {tonumber(x), tonumber(y), tonumber(z)}
                    _entities[nickname].rigidbody:set_body_type("kinematic")
                    _entities[nickname].rigidbody:set_gravity_scale({0, 0, 0})
                end
            elseif command == "st" then
                local seconds = args:match("(%S+)")
                if seconds ~= nil then 
                    world.set_day_time(tonumber(seconds)/1440)
                end
            elseif command == "rm" then
                local nickname, id = args:match("(%S+) (%S+)")
                if nickname ~= nil and id ~= nil and _entities[nickname] ~= nil then 
                    refresh_model(nickname,id)
                end
            elseif command == "dcon" then
                local nickname = args:match("(%S+)")	
                if _entities[nickname] ~= nil then
                    _entities[nickname]:despawn()
                    ent_uid =  _entities[nickname]:get_uid()
                    gfx.text3d.hide(fmp.playerdat[ent_uid].text_3d)
                    
                    print("despawn "..nickname)
                    _entities[nickname] = nil
                end
            end
        end
    end
end

function on_block_placed(block_id, x, y, z)
	local rot = block.get_rotation(x,y,z)
	print("POST bp "..block_id.." "..x.." "..y.." "..z..""..rot)
	place_block(block_id,x,y,z,rot)
end

function on_block_broken(block_id, x, y, z)
	print("POST bb "..block_id.." "..x.." "..y.." "..z)
	break_block(block_id,x,y,z)
end

function refresh_own_model(id)
    if socket and socket:is_connected() then
        local message = "rm "..id
        socket:send(message..";")
    end
end

function refresh_model(nickname, index_id)
    local rig = _entities[nickname].skeleton
    if index_id ~= 0 then
        itemIndex = rig:index("item")
        rig:set_model(itemIndex, item.model_name(index_id))
        rig:set_matrix(itemIndex, mat4.rotate({0, 1, 0}, -80))
    else
        ig:set_model(itemIndex, "")
    end
end

function place_block(block_id, x, y, z,rot)
    if socket and socket:is_connected() then
        local message = string.format("bp %s %d %d %d %d", block_id, x, y, z, rot)
        socket:send(message..";")
    end
end

function break_block(block_id, x, y, z)
    if socket and socket:is_connected() then
        local message = string.format("bb %s %d %d %d",  block_id, x, y, z)
        socket:send(message..";")
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
            return "Try connect. More information in console."
        end
    )
end
function on_world_tick()
    
    if connected == true then

        receive_data()

        local invid, slotid = player.get_inventory()
        local itemid, _ = inventory.get(invid, slotid)
        

        local x, y, z = player.get_pos()
        local x_angle, y_angle, z_angle = player.get_rot()
        local current_time = os.clock()


        if (math.abs(x - last_position.x) > movement_threshold or
            math.abs(y - last_position.y) > movement_threshold or
            math.abs(z - last_position.z) > movement_threshold or
            math.abs(x_angle - last_position.x_angle) > movement_threshold) and
            (current_time - last_update_time > update_interval) then
            socket:send("ep " .. math.floor(x*100)/100 .. " " .. math.floor(y*100)/100 .. " " .. math.floor(z*100)/100 .. " " .. (math.floor(x_angle*100)/100) .. ";")
            print("POST ep " .. x .. " " .. y .. " " .. z .. " " .. x_angle)
            last_position = {x = x, y = y, z = z, x_angle=x_angle}
            last_update_time = current_time 
        end

        if last_itemid ~= itemid then
            last_itemid = itemid
            refresh_own_model(itemid)
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