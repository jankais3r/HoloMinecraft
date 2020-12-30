#version 120

uniform float far;
uniform float near;
uniform int frameCounter;
uniform sampler2D gcolor;
uniform sampler2D depthtex0;
varying vec4 texcoord;

float getDepth(vec2 coord) {
	return 2.0 * near * far / (far + near - (2.0 * texture2D(depthtex0, coord).x - 1.0) * (far - near)) / far;
}

void main() {
	float depth = getDepth(texcoord.st);
	if(abs(mod(frameCounter, 2.0) - 1.0) < 0.00001) {
		gl_FragColor = vec4(depth, depth, depth, 1.0);
	} else {
		vec3 color = texture2D(gcolor, texcoord.st).rgb;
		gl_FragColor = vec4(color.rgb, 1.0);
	}
}