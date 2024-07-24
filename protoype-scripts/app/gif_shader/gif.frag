#version 330 core
out vec4 fragColor;

in vec2 fragUV;
uniform sampler2D gifTexture;

void main(){
    fragColor = texture(gifTexture, fragUV);
}