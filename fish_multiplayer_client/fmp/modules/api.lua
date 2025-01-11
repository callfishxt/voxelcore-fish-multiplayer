require "globals"

fmp_api = {}
fmp_api.block = {}


fmp_api.block.place = function (x, y, z, id)
    block.place(x,y,z,id)
end

fmp_api.block.destruct = function (x, y, z)
    block.destruct(x,y,z)
end

fmp_api.block.set_rotation = function (x,y,z,rotation)
    block.set_rotation(x,y,z,rotation)
    fmp.cfunc.block_rotate(x,y,z,rotation)
end

