# Reference — GLTF Animations with useAnimations

Part of the `r3f-animation` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## useFrame Basics

useFrame basics (state object, delta, priority) are covered in r3f-fundamentals — this skill assumes them.

## GLTF Animations with useAnimations

The recommended way to play animations from GLTF/GLB files.

### Basic Usage

```tsx
import { useGLTF, useAnimations } from '@react-three/drei'
import { useEffect, useRef } from 'react'

function AnimatedModel() {
  const group = useRef<THREE.Object3D>(null!)
  const { scene, animations } = useGLTF('/models/character.glb')
  const { actions, names } = useAnimations(animations, group)

  useEffect(() => {
    // Play first animation
    actions[names[0]]?.play()
  }, [actions, names])

  return <primitive ref={group} object={scene} />
}
```

### Animation Control

```tsx
function Character() {
  const group = useRef<THREE.Object3D>(null!)
  const { scene, animations } = useGLTF('/models/character.glb')
  const { actions, mixer } = useAnimations(animations, group)

  useEffect(() => {
    const action = actions['Walk']
    if (action) {
      // Playback control
      action.play()
      action.stop()
      action.reset()
      action.paused = true

      // Speed
      action.timeScale = 1.5  // 1.5x speed
      action.timeScale = -1   // Reverse

      // Loop modes
      action.loop = THREE.LoopOnce
      action.loop = THREE.LoopRepeat
      action.loop = THREE.LoopPingPong
      action.repetitions = 3
      action.clampWhenFinished = true

      // Weight (for blending)
      action.weight = 1
    }
  }, [actions])

  return <primitive ref={group} object={scene} />
}
```

### Crossfade Between Animations

```tsx
import { useGLTF, useAnimations } from '@react-three/drei'
import { useState, useEffect, useRef } from 'react'

function Character() {
  const group = useRef<THREE.Group>(null!)
  const { scene, animations } = useGLTF('/models/character.glb')
  const { actions } = useAnimations(animations, group)
  const [currentAnim, setCurrentAnim] = useState('Idle')

  useEffect(() => {
    // Fade out all animations
    Object.values(actions).forEach(action => {
      action?.fadeOut(0.5)
    })

    // Fade in current animation
    actions[currentAnim]?.reset().fadeIn(0.5).play()
  }, [currentAnim, actions])

  return (
    <group ref={group}>
      <primitive object={scene} />
    </group>
  )
}
```

### Animation Events

```tsx
function AnimatedModel() {
  const group = useRef<THREE.Object3D>(null!)
  const { scene, animations } = useGLTF('/models/character.glb')
  const { actions, mixer } = useAnimations(animations, group)

  useEffect(() => {
    // Listen for animation events
    const onFinished = (e) => {
      console.log('Animation finished:', e.action.getClip().name)
    }

    const onLoop = (e) => {
      console.log('Animation looped:', e.action.getClip().name)
    }

    mixer.addEventListener('finished', onFinished)
    mixer.addEventListener('loop', onLoop)

    return () => {
      mixer.removeEventListener('finished', onFinished)
      mixer.removeEventListener('loop', onLoop)
    }
  }, [mixer])

  return <primitive ref={group} object={scene} />
}
```

### Animation Blending

```tsx
function CharacterController({ speed = 0 }) {
  const group = useRef<THREE.Object3D>(null!)
  const { scene, animations } = useGLTF('/models/character.glb')
  const { actions } = useAnimations(animations, group)

  useEffect(() => {
    // Start all animations
    actions['Idle']?.play()
    actions['Walk']?.play()
    actions['Run']?.play()
  }, [actions])

  // Blend based on speed
  useFrame(() => {
    if (speed < 0.1) {
      actions['Idle']?.setEffectiveWeight(1)
      actions['Walk']?.setEffectiveWeight(0)
      actions['Run']?.setEffectiveWeight(0)
    } else if (speed < 5) {
      const t = speed / 5
      actions['Idle']?.setEffectiveWeight(1 - t)
      actions['Walk']?.setEffectiveWeight(t)
      actions['Run']?.setEffectiveWeight(0)
    } else {
      const t = Math.min((speed - 5) / 5, 1)
      actions['Idle']?.setEffectiveWeight(0)
      actions['Walk']?.setEffectiveWeight(1 - t)
      actions['Run']?.setEffectiveWeight(t)
    }
  })

  return <primitive ref={group} object={scene} />
}
```

