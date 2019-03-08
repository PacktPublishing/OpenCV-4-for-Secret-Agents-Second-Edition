Shader "Draw/Solid Color" {
	Properties {
		_Color ("Main Color", Color) = (1.0, 1.0, 1.0, 1.0)
	}
	SubShader {
		Pass { Color [_Color] }
	}
}
