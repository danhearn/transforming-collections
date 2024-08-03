#version 330 core
out vec4 fragColor;

in vec2 fragUV;
uniform sampler2D gifTexture;
uniform float tex_w;
uniform float tex_h;
uniform float window_w;
uniform float window_h;

void main(){
    vec2 uv = fragUV;
    float scale_x, scale_y = 1.0;
    float window_ratio = window_w / window_h;
    float tex_ratio = tex_w / tex_h;

    if (tex_ratio < 1.0) {
        if (tex_ratio < window_ratio) {
            scale_x = tex_h / tex_w * window_ratio;
            uv.x *= scale_x;
            uv.x += (1.0 - scale_x) / 2.0;
        } else{
            scale_y = tex_w / tex_h / window_ratio;
            uv.y *= scale_y;
            uv.y += (1.0 - scale_y) / 2.0;
        }
    }
    else if (tex_ratio > 1.0) {
        if (tex_ratio > window_ratio) {
            scale_y = tex_w / tex_h / window_ratio;
            uv.y *= scale_y;
            uv.y += (1.0 - scale_y) / 2.0;
        } else {
            scale_x = tex_h / tex_w * window_ratio;
            uv.x *= scale_x;
            uv.x += (1.0 - scale_x) / 2.0;
        }
    }
    else if (window_ratio < 1.0) {
        uv.y *= 1.0/window_ratio;
        uv.y += (1.0 - 1.0/window_ratio) / 2.0;
    }
    else if (window_ratio > 1.0) {
        uv.x *= window_ratio;
        uv.x += (1.0 - window_ratio) / 2.0;
    }

    fragColor = texture(gifTexture, uv);
}
