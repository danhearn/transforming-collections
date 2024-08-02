#version 330 core
out vec4 fragColor;

in vec2 fragUV;
uniform sampler2D gifTexture;
uniform float tex_w;
uniform float tex_h;

void main(){
    float screen_w = 400;
    float screen_h = 400;

    float scale_x = 1.0;
    float scale_y = 1.0;

    if (tex_w > tex_h) { // the texture is wider than it is tall
        scale_x = 1.0;
        scale_y = tex_w / tex_h; // smaller in proportion to the real dimensions
    } else if (tex_w < tex_h) { // the texture is taller than it is wide 
        scale_x = tex_h / tex_w;
        scale_y = 1.0;
    } 

    vec2 adjustedUV = fragUV * vec2(scale_x, scale_y);
    adjustedUV += vec2((1.0 - scale_x) / 2.0, (1.0 - scale_y) / 2.0);

    fragColor = texture(gifTexture, adjustedUV);
}