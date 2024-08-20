#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec2 uv;

uniform bool is_flipped;

out vec2 fragUV;

void main(){
    fragUV = uv;
    if (is_flipped){
        fragUV.y = 1.0 - fragUV.y;
    }
    gl_Position = vec4(position, 1.0);
}