#version 330 core

in vec2 fragUV;
out vec3 color;

void main(){
    color = vec3(fragUV, 1.0);
}