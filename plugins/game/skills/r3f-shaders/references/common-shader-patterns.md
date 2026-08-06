# Reference — Common Shader Patterns

Part of the `r3f-shaders` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Common Shader Patterns

### Texture Sampling

```tsx
import { useTexture } from '@react-three/drei'

function TexturedShaderMesh() {
  const texture = useTexture('/textures/color.jpg')
  const materialRef = useRef<THREE.ShaderMaterial>(null!)

  return (
    <mesh>
      <planeGeometry args={[2, 2]} />
      <myShaderMaterial ref={materialRef} map={texture} />
    </mesh>
  )
}

// Shader
const TextureMaterial = shaderMaterial(
  { map: null },
  `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  `
    uniform sampler2D map;
    varying vec2 vUv;

    void main() {
      vec4 texColor = texture2D(map, vUv);
      gl_FragColor = texColor;
    }
  `
)
```

### Vertex Displacement

```tsx
const WaveMaterial = shaderMaterial(
  { time: 0, amplitude: 0.5, frequency: 2.0 },
  `
    uniform float time;
    uniform float amplitude;
    uniform float frequency;
    varying vec2 vUv;

    void main() {
      vUv = uv;
      vec3 pos = position;

      // Wave displacement
      pos.z += sin(pos.x * frequency + time) * amplitude;
      pos.z += sin(pos.y * frequency + time) * amplitude;

      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
  `,
  `
    varying vec2 vUv;
    void main() {
      gl_FragColor = vec4(vUv, 1.0, 1.0);
    }
  `
)

extend({ WaveMaterial })

function WavePlane() {
  const ref = useRef<THREE.ShaderMaterial>(null!)

  useFrame(({ clock }) => {
    ref.current.time = clock.elapsedTime
  })

  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]}>
      <planeGeometry args={[10, 10, 64, 64]} />
      <waveMaterial ref={ref} />
    </mesh>
  )
}
```

### Fresnel Effect

```tsx
const FresnelMaterial = shaderMaterial(
  { fresnelColor: new THREE.Color('cyan'), baseColor: new THREE.Color('navy') },
  `
    varying vec3 vNormal;
    varying vec3 vWorldPosition;

    void main() {
      vNormal = normalize(normalMatrix * normal);
      vWorldPosition = (modelMatrix * vec4(position, 1.0)).xyz;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  `
    uniform vec3 fresnelColor;
    uniform vec3 baseColor;
    varying vec3 vNormal;
    varying vec3 vWorldPosition;

    void main() {
      vec3 viewDirection = normalize(cameraPosition - vWorldPosition);
      float fresnel = pow(1.0 - dot(viewDirection, vNormal), 3.0);

      gl_FragColor = vec4(mix(baseColor, fresnelColor, fresnel), 1.0);
    }
  `
)
```

### Noise Functions

```glsl
// Simple random
float random(vec2 st) {
  return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453);
}

// Value noise
float noise(vec2 st) {
  vec2 i = floor(st);
  vec2 f = fract(st);

  float a = random(i);
  float b = random(i + vec2(1.0, 0.0));
  float c = random(i + vec2(0.0, 1.0));
  float d = random(i + vec2(1.0, 1.0));

  vec2 u = f * f * (3.0 - 2.0 * f);

  return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}

// FBM (Fractal Brownian Motion)
float fbm(vec2 st) {
  float value = 0.0;
  float amplitude = 0.5;

  for (int i = 0; i < 5; i++) {
    value += amplitude * noise(st);
    st *= 2.0;
    amplitude *= 0.5;
  }

  return value;
}
```

### Gradient

```glsl
// Linear gradient
vec3 gradient = mix(colorA, colorB, vUv.y);

// Radial gradient
float dist = distance(vUv, vec2(0.5));
vec3 radial = mix(centerColor, edgeColor, dist * 2.0);

// Smooth gradient
float t = smoothstep(0.0, 1.0, vUv.y);
vec3 smooth = mix(colorA, colorB, t);
```

### Dissolve Effect

```tsx
const DissolveMaterial = shaderMaterial(
  { progress: 0, noiseScale: 10.0, edgeColor: new THREE.Color('orange') },
  `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  `
    uniform float progress;
    uniform float noiseScale;
    uniform vec3 edgeColor;
    varying vec2 vUv;

    float random(vec2 st) {
      return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453);
    }

    float noise(vec2 st) {
      vec2 i = floor(st);
      vec2 f = fract(st);
      float a = random(i);
      float b = random(i + vec2(1.0, 0.0));
      float c = random(i + vec2(0.0, 1.0));
      float d = random(i + vec2(1.0, 1.0));
      vec2 u = f * f * (3.0 - 2.0 * f);
      return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
    }

    void main() {
      float n = noise(vUv * noiseScale);

      if (n < progress) {
        discard;
      }

      float edge = smoothstep(progress, progress + 0.1, n);
      vec3 baseColor = vec3(0.5);

      gl_FragColor = vec4(mix(edgeColor, baseColor, edge), 1.0);
    }
  `
)
```

