#version 330 core
out vec4 fragColor;

in vec2 fragUV;
uniform sampler2D gifTexture;
uniform float tex_w;
uniform float tex_h;

void main(){
    float screen_w = 400;
    float screen_h = 400;

    float scaleX = 2.;
    float scaleY = 1.0;

    vec2 adjustedUV = fragUV * vec2(scaleX, scaleY);

    adjustedUV += vec2((1.0 - scaleX) / 2.0, (1.0 - scaleY) / 2.0);

    fragColor = texture(gifTexture, adjustedUV);
}