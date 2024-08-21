#version 330 core
out vec4 fragColor;

in vec2 fragUV;
uniform sampler2D media_texture;
uniform float tex_w;
uniform float tex_h;
uniform float window_w;
uniform float window_h;

void main(){
    vec2 uv = fragUV;
    vec2 scale = vec2(1.0, 1.0);
    
    float window_ratio = window_w / window_h;
    float tex_ratio = tex_w / tex_h;

    if (tex_ratio < window_ratio) {
        scale.x = tex_h / tex_w * window_ratio;
    } else if (tex_ratio > window_ratio) {
        scale.y = tex_w / tex_h / window_ratio;
    }

    uv *= scale;
    uv += (1.0 - scale) / 2.0;

    vec4 color = texture(media_texture, uv);
    fragColor = color;
}