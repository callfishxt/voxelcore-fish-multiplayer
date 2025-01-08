require "globals"

local movementSpeed = 5
local rotationSpeedFactor = 0.2

local currentAngle = 0
local desiredAngle = 0


function on_render()
    local playerData = fetchPlayerData(entity:get_uid())
    if not playerData then
        entity:despawn()
        return
    end

    moveEntityTowardsTarget(playerData.position)
    if playerData.body_rotation ~= nil then
        updateEntityRotation(tonumber(playerData.body_rotation))
    end
    
    pos = entity.transform:get_pos()
    gfx.text3d.set_pos(playerData.text_3d,{pos[1],pos[2]+1.25,pos[3]})
end


function fetchPlayerData(uid)
    return fmp.playerdat[uid]
end

function moveEntityTowardsTarget(targetPosition)
    local currentPos = entity.transform:get_pos()
    local movementDirection = calculateDirection(currentPos, targetPosition)
    
    entity.rigidbody:set_vel({
        movementDirection[1] * movementSpeed,
        movementDirection[2] * movementSpeed,
        movementDirection[3] * movementSpeed
    })
end


function calculateDirection(currentPos, targetPos)
    return {
        targetPos[1] - currentPos[1],
        targetPos[2] - currentPos[2],
        targetPos[3] - currentPos[3]
    }
end

function updateEntityRotation(targetRotation)
    desiredAngle = targetRotation
    currentAngle = smoothRotation(currentAngle, desiredAngle, rotationSpeedFactor)
    entity.transform:set_rot(mat4.rotate({0, 1, 0}, currentAngle))
end

function smoothRotation(startAngle, endAngle, factor)
    local angleDifference = endAngle - startAngle

    if math.abs(angleDifference) > 180 then
        endAngle = endAngle + (angleDifference > 0 and -360 or 360)
    end

    return startAngle + (endAngle - startAngle) * factor
end