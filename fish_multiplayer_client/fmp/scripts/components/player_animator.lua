require "globals"

local movementSpeed = 8
local rotationSpeedFactor = 0.2

local BodyAngle = 0

local HeadAngle = 0

function on_render()
    local playerData = fmp.playerdat[entity:get_uid()]
    if not playerData then
        entity:despawn()
        return
    end

    local currentPos = entity.transform:get_pos()
    entity.rigidbody:set_vel({
        (playerData.position[1] - currentPos[1]) * movementSpeed,
        (playerData.position[2] - currentPos[2]) * movementSpeed, 
        (playerData.position[3] - currentPos[3]) * movementSpeed
    })

    if playerData.body_rotation ~= nil then
        updateBodyRotation(tonumber(playerData.body_rotation))
    end
    
    if playerData.head_rotation ~= nil then
        updateHeadRotation(tonumber(playerData.head_rotation))
    end

    pos = entity.transform:get_pos()
    gfx.text3d.set_pos(playerData.text_3d,{pos[1],pos[2]+1.25,pos[3]})
end

function updateBodyRotation(targetRotation)
    BodyAngle = smoothRotation(BodyAngle, targetRotation, rotationSpeedFactor)
    entity.transform:set_rot(mat4.rotate({0, 1, 0}, BodyAngle))
end

function updateHeadRotation(targetRotation)
    HeadAngle = HeadAngle + (targetRotation - HeadAngle) * rotationSpeedFactor
    entity.skeleton:set_matrix(entity.skeleton:index("head"), mat4.rotate({1, 0, 0}, HeadAngle))
end

function smoothRotation(startAngle, endAngle, factor)
    local angleDifference = endAngle - startAngle

    if math.abs(angleDifference) > 180 then
        endAngle = endAngle + (angleDifference > 0 and -360 or 360)
    end

    return startAngle + (endAngle - startAngle) * factor
end