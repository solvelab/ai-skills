# Reference — Custom Effects

Part of the `r3f-postprocessing` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Combining Multiple Effects

```tsx
import { EffectComposer, Bloom, Vignette, ChromaticAberration, Noise, SMAA } from '@react-three/postprocessing'
import { BlendFunction } from 'postprocessing'

function PostProcessing() {
  return (
    <EffectComposer multisampling={0}>
      {/* Glow effect */}
      <Bloom
        intensity={1.5}
        luminanceThreshold={0.9}
        luminanceSmoothing={0.025}
        mipmapBlur
      />

      {/* Color aberration */}
      <ChromaticAberration
        offset={[0.001, 0.001]}
        radialModulation
        modulationOffset={0.5}
      />

      {/* Film grain */}
      <Noise
        premultiply
        blendFunction={BlendFunction.ADD}
        opacity={0.2}
      />

      {/* Vignette */}
      <Vignette
        offset={0.3}
        darkness={0.5}
      />

      {/* Anti-aliasing (should be last) */}
      <SMAA />
    </EffectComposer>
  )
}
```

## Custom Effects

### Using postprocessing Effect Class

```tsx
// excerpt — not a complete module; see the surrounding section for context
import { forwardRef, useMemo } from 'react'
import { Effect, BlendFunction } from 'postprocessing'
import { Uniform } from 'three'

// Fragment shader
const fragmentShader = `
  uniform float time;
  uniform float intensity;

  void mainImage(const in vec4 inputColor, const in vec2 uv, out vec4 outputColor) {
    vec2 distortedUv = uv;
    distortedUv.x += sin(uv.y * 10.0 + time) * 0.01 * intensity;

    vec4 color = texture2D(inputBuffer, distortedUv);
    outputColor = color;
  }
`

// Effect class
class WaveDistortionEffect extends Effect {
  constructor({ intensity = 1.0, blendFunction = BlendFunction.NORMAL } = {}) {
    super('WaveDistortionEffect', fragmentShader, {
      blendFunction,
      uniforms: new Map([
        ['time', new Uniform(0)],
        ['intensity', new Uniform(intensity)],
      ]),
    })
  }

  update(renderer, inputBuffer, deltaTime) {
    this.uniforms.get('time').value += deltaTime
  }
}

// React component wrapper
export const WaveDistortion = forwardRef(({ intensity = 1.0, blendFunction }, ref) => {
  const effect = useMemo(() => new WaveDistortionEffect({ intensity, blendFunction }), [intensity, blendFunction])
  return <primitive ref={ref} object={effect} dispose={null} />
})

// Usage
<EffectComposer>
  <WaveDistortion intensity={0.5} />
</EffectComposer>
```

### Shader with wrapEffect

```tsx
// excerpt — not a complete module; see the surrounding section for context
import { wrapEffect } from '@react-three/postprocessing'
import { Effect, BlendFunction } from 'postprocessing'
import { Uniform } from 'three'

class InvertEffect extends Effect {
  constructor({ blendFunction = BlendFunction.NORMAL } = {}) {
    super('InvertEffect', `
      void mainImage(const in vec4 inputColor, const in vec2 uv, out vec4 outputColor) {
        outputColor = vec4(1.0 - inputColor.rgb, inputColor.a);
      }
    `, {
      blendFunction,
    })
  }
}

export const Invert = wrapEffect(InvertEffect)

// Usage
<EffectComposer>
  <Invert />
</EffectComposer>
```

## Conditional Effects

```tsx
import { useState } from 'react'
import { EffectComposer, Bloom, Vignette, Glitch } from '@react-three/postprocessing'

function ConditionalPostProcessing() {
  const [effects, setEffects] = useState({
    bloom: true,
    vignette: true,
    glitch: false,
  })

  return (
    <>
      <EffectComposer>
        {effects.bloom && (
          <Bloom intensity={1.5} luminanceThreshold={0.9} />
        )}
        {effects.vignette && (
          <Vignette offset={0.5} darkness={0.5} />
        )}
        {effects.glitch && (
          <Glitch delay={[1, 3]} duration={[0.5, 1]} strength={[0.3, 1]} />
        )}
      </EffectComposer>

      {/* UI to toggle effects */}
      <div className="controls">
        <button onClick={() => setEffects(e => ({ ...e, bloom: !e.bloom }))}>
          Toggle Bloom
        </button>
        <button onClick={() => setEffects(e => ({ ...e, vignette: !e.vignette }))}>
          Toggle Vignette
        </button>
        <button onClick={() => setEffects(e => ({ ...e, glitch: !e.glitch }))}>
          Toggle Glitch
        </button>
      </div>
    </>
  )
}
```

## Animated Effects

```tsx
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { EffectComposer, Bloom, ChromaticAberration } from '@react-three/postprocessing'

function AnimatedEffects() {
  const bloomRef = useRef<React.ComponentRef<typeof Bloom>>(null!)
  const chromaticRef = useRef<React.ComponentRef<typeof ChromaticAberration>>(null!)

  useFrame(({ clock }) => {
    const t = clock.elapsedTime

    // Animate bloom intensity
    if (bloomRef.current) {
      bloomRef.current.intensity = 1 + Math.sin(t) * 0.5
    }

    // Animate chromatic aberration
    if (chromaticRef.current) {
      const offset = Math.sin(t * 2) * 0.002
      chromaticRef.current.offset.set(offset, offset)
    }
  })

  return (
    <EffectComposer>
      <Bloom ref={bloomRef} luminanceThreshold={0.9} />
      <ChromaticAberration ref={chromaticRef} />
    </EffectComposer>
  )
}
```

## N8AO (High Quality AO)

```tsx
import { EffectComposer } from '@react-three/postprocessing'
import { N8AO } from '@react-three/postprocessing'

<EffectComposer>
  <N8AO
    aoRadius={0.5}
    intensity={1}
    aoSamples={6}
    denoiseSamples={4}
    denoiseRadius={12}
    distanceFalloff={1}
    color="black"
    quality="low"   // low, medium, high, ultra
    halfRes={false}
  />
</EffectComposer>
```

