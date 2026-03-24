---
name: r3f-animation
description: React Three Fiber animation - useFrame, useAnimations, spring physics, keyframes. Use when animating objects, playing GLTF animations, creating procedural motion, or implementing physics-based movement.
---

# React Three Fiber Animation

## Quick Start

```tsx
import { Canvas, useFrame } from '@react-three/fiber'
import { useRef } from 'react'

function RotatingBox() {
  const meshRef = useRef()

  useFrame((state, delta) => {
    meshRef.current.rotation.x += delta
    meshRef.current.rotation.y += delta * 0.5
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="hotpink" />
    </mesh>
  )
}

export default function App() {
  return (
    <Canvas>
      <ambientLight />
      <RotatingBox />
    </Canvas>
  )
}
```

## useFrame Hook

The core animation hook in R3F. Runs every frame.

### Basic Usage

```tsx
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'

function AnimatedMesh() {
  const meshRef = useRef()

  useFrame((state, delta) => {
    // state contains: clock, camera, scene, gl, mouse, etc.
    // delta is time since last frame in seconds

    meshRef.current.rotation.y += delta
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
}
```

### State Object

```tsx
useFrame((state, delta, xrFrame) => {
  const {
    clock,           // THREE.Clock
    camera,          // Current camera
    scene,           // Scene
    gl,              // WebGLRenderer
    mouse,           // Normalized mouse position (-1 to 1)
    pointer,         // Same as mouse
    viewport,        // Viewport dimensions
    size,            // Canvas size
    raycaster,       // Raycaster
    get,             // Get current state
    set,             // Set state
    invalidate,      // Request re-render (when frameloop="demand")
  } = state

  // Time-based animation
  const t = clock.getElapsedTime()
  meshRef.current.position.y = Math.sin(t) * 2
})
```

### Render Priority

```tsx
// Lower numbers run first. Default is 0.
// Use negative for pre-render, positive for post-render

function PreRender() {
  useFrame(() => {
    // Runs before main render
  }, -1)
}

function PostRender() {
  useFrame(() => {
    // Runs after main render
  }, 1)
}

function DefaultRender() {
  useFrame(() => {
    // Runs at default priority (0)
  })
}
```

### Conditional Animation

```tsx
function ConditionalAnimation({ isAnimating }) {
  const meshRef = useRef()

  useFrame((state, delta) => {
    if (!isAnimating) return
    meshRef.current.rotation.y += delta
  })

  return <mesh ref={meshRef}>...</mesh>
}
```

## GLTF Animations with useAnimations

The recommended way to play animations from GLTF/GLB files.

### Basic Usage

```tsx
import { useGLTF, useAnimations } from '@react-three/drei'
import { useEffect, useRef } from 'react'

function AnimatedModel() {
  const group = useRef()
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
  const group = useRef()
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
  const group = useRef()
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
  const group = useRef()
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
  const group = useRef()
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

## Spring Animation (@react-spring/three)

Physics-based spring animations that integrate with R3F.

### Installation

```bash
npm install @react-spring/three
```

### Basic Spring

```tsx
import { useSpring, animated } from '@react-spring/three'

function AnimatedBox() {
  const [active, setActive] = useState(false)

  const { scale, color } = useSpring({
    scale: active ? 1.5 : 1,
    color: active ? '#ff6b6b' : '#4ecdc4',
    config: { mass: 1, tension: 280, friction: 60 }
  })

  return (
    <animated.mesh
      scale={scale}
      onClick={() => setActive(!active)}
    >
      <boxGeometry />
      <animated.meshStandardMaterial color={color} />
    </animated.mesh>
  )
}
```

### Spring Config Presets

```tsx
import { useSpring, animated, config } from '@react-spring/three'

function SpringPresets() {
  const { position } = useSpring({
    position: [0, 2, 0],
    config: config.wobbly  // Presets: default, gentle, wobbly, stiff, slow, molasses
  })

  // Or custom config
  const { rotation } = useSpring({
    rotation: [0, Math.PI, 0],
    config: {
      mass: 1,
      tension: 170,
      friction: 26,
      clamp: false,
      precision: 0.01,
      velocity: 0,
    }
  })

  return (
    <animated.mesh position={position} rotation={rotation}>
      <boxGeometry />
      <meshStandardMaterial />
    </animated.mesh>
  )
}
```

### Multiple Springs

```tsx
import { useSprings, animated } from '@react-spring/three'

function AnimatedBoxes({ count = 5 }) {
  const [springs, api] = useSprings(count, (i) => ({
    position: [i * 2 - count, 0, 0],
    scale: 1,
    config: { mass: 1, tension: 280, friction: 60 }
  }))

  const handleClick = (index) => {
    api.start((i) => {
      if (i === index) return { scale: 1.5 }
      return { scale: 1 }
    })
  }

  return springs.map((spring, i) => (
    <animated.mesh
      key={i}
      position={spring.position}
      scale={spring.scale}
      onClick={() => handleClick(i)}
    >
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </animated.mesh>
  ))
}
```

### Gesture Integration

```tsx
import { useSpring, animated } from '@react-spring/three'
import { useDrag } from '@use-gesture/react'

function DraggableBox() {
  const [spring, api] = useSpring(() => ({
    position: [0, 0, 0],
    config: { mass: 1, tension: 280, friction: 60 }
  }))

  const bind = useDrag(({ movement: [mx, my], down }) => {
    api.start({
      position: down ? [mx / 100, -my / 100, 0] : [0, 0, 0]
    })
  })

  return (
    <animated.mesh {...bind()} position={spring.position}>
      <boxGeometry />
      <meshStandardMaterial color="hotpink" />
    </animated.mesh>
  )
}
```

### Chain Animations

```tsx
import { useSpring, animated, useChain, useSpringRef } from '@react-spring/three'

function ChainedAnimation() {
  const scaleRef = useSpringRef()
  const rotationRef = useSpringRef()

  const { scale } = useSpring({
    ref: scaleRef,
    from: { scale: 0 },
    to: { scale: 1 },
    config: { tension: 200, friction: 20 }
  })

  const { rotation } = useSpring({
    ref: rotationRef,
    from: { rotation: [0, 0, 0] },
    to: { rotation: [0, Math.PI * 2, 0] },
    config: { tension: 100, friction: 30 }
  })

  // Scale first (0-0.5), then rotation (0.5-1)
  useChain([scaleRef, rotationRef], [0, 0.5])

  return (
    <animated.mesh scale={scale} rotation={rotation}>
      <boxGeometry />
      <meshStandardMaterial color="cyan" />
    </animated.mesh>
  )
}
```

## Morph Targets

Blend between different mesh shapes.

```tsx
import { useGLTF } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'

function MorphingFace() {
  const { scene, nodes } = useGLTF('/models/face.glb')
  const meshRef = useRef()

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime()

    // Access morph target influences
    if (meshRef.current?.morphTargetInfluences) {
      // Animate smile
      const smileIndex = meshRef.current.morphTargetDictionary['smile']
      meshRef.current.morphTargetInfluences[smileIndex] = (Math.sin(t) + 1) / 2
    }
  })

  return (
    <primitive ref={meshRef} object={nodes.Face} />
  )
}
```

### Controlled Morph Targets

```tsx
function MorphControls({ morphInfluences }) {
  const { nodes } = useGLTF('/models/face.glb')
  const meshRef = useRef()

  useFrame(() => {
    if (meshRef.current?.morphTargetInfluences) {
      Object.entries(morphInfluences).forEach(([name, value]) => {
        const index = meshRef.current.morphTargetDictionary[name]
        if (index !== undefined) {
          meshRef.current.morphTargetInfluences[index] = value
        }
      })
    }
  })

  return <primitive ref={meshRef} object={nodes.Face} />
}

// Usage
<MorphControls morphInfluences={{ smile: 0.5, blink: 1, angry: 0 }} />
```

## Skeletal Animation

### Accessing Bones

```tsx
import { useGLTF } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useEffect, useRef } from 'react'

function SkeletalCharacter() {
  const { scene } = useGLTF('/models/character.glb')
  const headBoneRef = useRef()

  useEffect(() => {
    // Find skeleton
    scene.traverse((child) => {
      if (child.isSkinnedMesh) {
        const skeleton = child.skeleton
        const headBone = skeleton.bones.find(b => b.name === 'Head')
        headBoneRef.current = headBone
      }
    })
  }, [scene])

  // Animate bone
  useFrame(({ clock }) => {
    if (headBoneRef.current) {
      headBoneRef.current.rotation.y = Math.sin(clock.elapsedTime) * 0.3
    }
  })

  return <primitive object={scene} />
}
```

### Bone Attachments

```tsx
function CharacterWithWeapon() {
  const { scene } = useGLTF('/models/character.glb')
  const weaponRef = useRef()
  const handBoneRef = useRef()

  useEffect(() => {
    scene.traverse((child) => {
      if (child.isSkinnedMesh) {
        const handBone = child.skeleton.bones.find(b => b.name === 'RightHand')
        if (handBone && weaponRef.current) {
          handBone.add(weaponRef.current)
          handBoneRef.current = handBone
        }
      }
    })

    return () => {
      // Cleanup
      if (handBoneRef.current && weaponRef.current) {
        handBoneRef.current.remove(weaponRef.current)
      }
    }
  }, [scene])

  return (
    <>
      <primitive object={scene} />
      <mesh ref={weaponRef} position={[0, 0, 0.5]}>
        <boxGeometry args={[0.1, 0.1, 1]} />
        <meshStandardMaterial color="gray" />
      </mesh>
    </>
  )
}
```

## Procedural Animation Patterns

### Smooth Damping

```tsx
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'
import * as THREE from 'three'

function SmoothFollow({ target }) {
  const meshRef = useRef()
  const currentPos = useRef(new THREE.Vector3())

  useFrame((state, delta) => {
    // Lerp towards target
    currentPos.current.lerp(target, delta * 5)
    meshRef.current.position.copy(currentPos.current)
  })

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[0.5]} />
      <meshStandardMaterial color="blue" />
    </mesh>
  )
}
```

### Spring Physics (Manual)

```tsx
function SpringMesh({ target = 0 }) {
  const meshRef = useRef()
  const spring = useRef({
    position: 0,
    velocity: 0,
    stiffness: 100,
    damping: 10
  })

  useFrame((state, delta) => {
    const s = spring.current
    const force = -s.stiffness * (s.position - target)
    const dampingForce = -s.damping * s.velocity

    s.velocity += (force + dampingForce) * delta
    s.position += s.velocity * delta

    meshRef.current.position.y = s.position
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="green" />
    </mesh>
  )
}
```

### Oscillation Patterns

```tsx
function OscillatingMesh() {
  const meshRef = useRef()

  useFrame(({ clock }) => {
    const t = clock.elapsedTime

    // Sine wave
    meshRef.current.position.y = Math.sin(t * 2) * 0.5

    // Circular motion
    meshRef.current.position.x = Math.cos(t) * 2
    meshRef.current.position.z = Math.sin(t) * 2

    // Bouncing
    meshRef.current.position.y = Math.abs(Math.sin(t * 3)) * 2

    // Figure 8
    meshRef.current.position.x = Math.sin(t) * 2
    meshRef.current.position.z = Math.sin(t * 2) * 1
  })

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[0.3]} />
      <meshStandardMaterial color="purple" />
    </mesh>
  )
}
```

## Drei Animation Helpers

### Float

```tsx
import { Float } from '@react-three/drei'

function FloatingObject() {
  return (
    <Float
      speed={1}            // Animation speed
      rotationIntensity={1} // Rotation intensity
      floatIntensity={1}   // Float intensity
      floatingRange={[-0.1, 0.1]} // Range of y-axis float
    >
      <mesh>
        <boxGeometry />
        <meshStandardMaterial color="gold" />
      </mesh>
    </Float>
  )
}
```

### MeshWobbleMaterial / MeshDistortMaterial

```tsx
import { MeshWobbleMaterial, MeshDistortMaterial } from '@react-three/drei'

function WobblyMesh() {
  return (
    <mesh>
      <torusKnotGeometry args={[1, 0.4, 100, 16]} />
      <MeshWobbleMaterial
        factor={1}     // Wobble amplitude
        speed={2}      // Wobble speed
        color="hotpink"
      />
    </mesh>
  )
}

function DistortedMesh() {
  return (
    <mesh>
      <sphereGeometry args={[1, 64, 64]} />
      <MeshDistortMaterial
        distort={0.5}  // Distortion amount
        speed={2}      // Animation speed
        color="cyan"
      />
    </mesh>
  )
}
```

### Trail

```tsx
import { Trail } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'

function TrailingMesh() {
  const meshRef = useRef()

  useFrame(({ clock }) => {
    const t = clock.elapsedTime
    meshRef.current.position.x = Math.sin(t) * 3
    meshRef.current.position.y = Math.cos(t * 2) * 2
  })

  return (
    <Trail
      width={2}
      length={8}
      color="hotpink"
      attenuation={(t) => t * t}
    >
      <mesh ref={meshRef}>
        <sphereGeometry args={[0.2]} />
        <meshStandardMaterial color="white" />
      </mesh>
    </Trail>
  )
}
```

## Animation with Zustand State

```tsx
import { create } from 'zustand'
import { useFrame } from '@react-three/fiber'

const useStore = create((set) => ({
  isAnimating: false,
  speed: 1,
  toggleAnimation: () => set((state) => ({ isAnimating: !state.isAnimating })),
  setSpeed: (speed) => set({ speed })
}))

function AnimatedMesh() {
  const meshRef = useRef()
  const { isAnimating, speed } = useStore()

  useFrame((state, delta) => {
    if (isAnimating) {
      meshRef.current.rotation.y += delta * speed
    }
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
}

// UI Component
function Controls() {
  const { toggleAnimation, setSpeed } = useStore()

  return (
    <div>
      <button onClick={toggleAnimation}>Toggle</button>
      <input
        type="range"
        min="0"
        max="5"
        step="0.1"
        onChange={(e) => setSpeed(parseFloat(e.target.value))}
      />
    </div>
  )
}
```

## State Management Performance

Critical patterns for high-performance state management in animations.

### getState() in useFrame

Use `getState()` instead of hooks inside useFrame for zero subscription overhead:

```tsx
import { create } from 'zustand'

const useGameStore = create((set) => ({
  playerPosition: [0, 0, 0],
  targetPosition: [0, 0, 0],
  setPlayerPosition: (pos) => set({ playerPosition: pos }),
}))

function Player() {
  const meshRef = useRef()

  useFrame((state, delta) => {
    // ✅ GOOD: getState() has no subscription overhead
    const { targetPosition } = useGameStore.getState()

    // Lerp towards target
    meshRef.current.position.lerp(
      new THREE.Vector3(...targetPosition),
      delta * 5
    )
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="blue" />
    </mesh>
  )
}
```

### Transient Subscriptions

Subscribe to state changes without triggering React re-renders:

```tsx
import { useEffect, useRef } from 'react'

function Enemy() {
  const meshRef = useRef()

  useEffect(() => {
    // Subscribe directly - updates mesh without re-rendering component
    const unsub = useGameStore.subscribe(
      (state) => state.playerPosition,
      (playerPos) => {
        // Look at player (runs on every state change, no re-render)
        meshRef.current.lookAt(...playerPos)
      }
    )
    return unsub
  }, [])

  return (
    <mesh ref={meshRef}>
      <coneGeometry args={[0.5, 1, 4]} />
      <meshStandardMaterial color="red" />
    </mesh>
  )
}
```

### Selective Subscriptions with Shallow

Subscribe to multiple values efficiently:

```tsx
import { shallow } from 'zustand/shallow'

function HUD() {
  // Only re-renders when health OR score actually changes
  const { health, score } = useGameStore(
    (state) => ({ health: state.health, score: state.score }),
    shallow
  )

  return (
    <Html>
      <div>Health: {health}</div>
      <div>Score: {score}</div>
    </Html>
  )
}

// For single values, no shallow needed
const health = useGameStore((state) => state.health)
```

### Isolate Animated Components

Separate state-dependent UI from animated 3D objects:

```tsx
// ❌ BAD: Parent re-renders cause animation jank
function BadPattern() {
  const [score, setScore] = useState(0)
  const meshRef = useRef()

  useFrame((_, delta) => {
    meshRef.current.rotation.y += delta  // Affected by score re-renders
  })

  return (
    <>
      <mesh ref={meshRef}>...</mesh>
      <ScoreDisplay score={score} />
    </>
  )
}

// ✅ GOOD: Isolated animation component
function GoodPattern() {
  return (
    <>
      <AnimatedMesh />      {/* Never re-renders from score */}
      <ScoreDisplay />      {/* Has its own state subscription */}
    </>
  )
}

function AnimatedMesh() {
  const meshRef = useRef()

  useFrame((_, delta) => {
    meshRef.current.rotation.y += delta  // Smooth, uninterrupted
  })

  return <mesh ref={meshRef}>...</mesh>
}

function ScoreDisplay() {
  const score = useGameStore((state) => state.score)
  return <Html><div>Score: {score}</div></Html>
}
```

## Performance Tips

1. **Isolate animated components**: Only the animated mesh re-renders
2. **Use refs over state**: Avoid React re-renders for animations
3. **Throttle expensive calculations**: Use delta accumulation
4. **Pause offscreen animations**: Check visibility
5. **Share animation clips**: Same clip for multiple instances

```tsx
// Isolate animation to prevent parent re-renders
function Scene() {
  return (
    <>
      <StaticMesh />   {/* Never re-renders */}
      <AnimatedMesh /> {/* Only this updates */}
    </>
  )
}

// Throttle expensive operations
function ThrottledAnimation() {
  const meshRef = useRef()
  const accumulated = useRef(0)

  useFrame((state, delta) => {
    accumulated.current += delta

    // Only update every 100ms
    if (accumulated.current > 0.1) {
      // Expensive calculation here
      accumulated.current = 0
    }

    // Cheap operations every frame
    meshRef.current.rotation.y += delta
  })
}
```

## Procedural Walk Cycle (Bipedal Character)

Complete procedural walk animation for low-poly humanoid characters using sine waves and biomechanical principles. No skeleton or GLTF required — works with primitive geometry groups.

### Biomechanical Reference Values

| Parameter | Value | Source |
|-----------|-------|--------|
| Walk cycle duration | 1.0–1.3s (2 steps) | Biomechanics standard |
| Steps per minute | 50–75 (natural walk) | mocaponline.com |
| Leg swing arc | 30–45° per direction | Animation reference |
| Arm swing arc | 25–35° (slightly less than legs) | Counter-motion principle |
| Body bob frequency | 2× leg frequency (bounce per step) | littlepolygon.com |
| Hip sway frequency | 0.5× leg frequency | littlepolygon.com |
| Torso counter-rotation | Opposes hip sway for balance | slynyrd.com |

### Key Principles

1. **Phase-locked to movement**: Walk phase advances with `delta`, not `clock.getElapsedTime()`. This prevents animation when stationary.
2. **Body bob**: Vertical bounce at 2× leg frequency — body rises at mid-step, falls at heel contact.
3. **Hip sway**: Lateral roll at half the leg frequency — left-right-left cadence.
4. **Torso counter-rotation**: Z-rotation opposes hip sway to maintain visual balance.
5. **Torso twist**: Y-rotation follows arm swing direction for natural spine movement.
6. **Arms oppose legs**: Right arm forward when left leg forward (counter-motion).
7. **Smooth blend**: Use `walkBlend` (0→1) to transition between idle and walk states smoothly — prevents animation snapping.
8. **Head bob**: Very subtle, follows body bob at reduced amplitude.

### Complete Implementation

```tsx
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

// Walk cycle parameters (tuned for ~0.8 scale humanoid)
const WALK_FREQ = 5.5;           // ~1.14s per cycle = natural walk
const LEG_AMPLITUDE = 0.55;      // ~31° swing each direction
const ARM_AMPLITUDE = 0.45;      // ~26° swing, slightly less than legs
const BODY_BOB_HEIGHT = 0.03;    // vertical bounce amplitude
const BODY_BOB_FREQ = 2;         // 2x leg frequency (bounce per step)
const HIP_SWAY_AMPLITUDE = 0.025; // subtle lateral sway
const HIP_SWAY_FREQ = 0.5;      // half leg frequency
const TORSO_COUNTER_ROT = 0.08;  // torso Z opposes hip sway
const TORSO_TWIST = 0.06;        // torso Y-rotation with arm swing
const HEAD_BOB = 0.008;          // very subtle head vertical motion

// Idle parameters
const IDLE_SWAY_FREQ = 1.0;
const IDLE_SWAY_AMP = 0.012;
const IDLE_BREATHE_FREQ = 0.8;
const IDLE_BREATHE_AMP = 0.005;

function smoothDamp(current: number, target: number, speed: number): number {
  return current + (target - current) * speed;
}

export function WalkingCharacter() {
  const groupRef = useRef<THREE.Group>(null);
  const bodyRef = useRef<THREE.Group>(null);
  const torsoRef = useRef<THREE.Group>(null);
  const headRef = useRef<THREE.Mesh>(null);
  const leftLegRef = useRef<THREE.Group>(null);
  const rightLegRef = useRef<THREE.Group>(null);
  const leftArmRef = useRef<THREE.Group>(null);
  const rightArmRef = useRef<THREE.Group>(null);

  const prevPos = useRef(new THREE.Vector3());
  const targetRotation = useRef(0);
  const walkPhase = useRef(0);
  const walkBlend = useRef(0); // 0=idle, 1=walking

  useFrame(({ clock }, delta) => {
    if (!groupRef.current || !bodyRef.current) return;
    const t = clock.getElapsedTime();

    // --- Detect movement ---
    const currentPos = groupRef.current.position;
    const dx = currentPos.x - prevPos.current.x;
    const dz = currentPos.z - prevPos.current.z;
    const speed = Math.sqrt(dx * dx + dz * dz);
    const isWalking = speed > 0.001;
    prevPos.current.copy(currentPos);

    // Smooth walk blend (prevents snapping)
    walkBlend.current = smoothDamp(walkBlend.current, isWalking ? 1 : 0, 0.1);
    const wb = walkBlend.current;

    // Advance phase only when moving (phase-locked)
    if (isWalking) walkPhase.current += WALK_FREQ * delta;
    const phase = walkPhase.current;

    // --- Rotation toward movement direction ---
    if (isWalking) targetRotation.current = Math.atan2(dx, dz);
    let diff = targetRotation.current - bodyRef.current.rotation.y;
    while (diff > Math.PI) diff -= Math.PI * 2;
    while (diff < -Math.PI) diff += Math.PI * 2;
    bodyRef.current.rotation.y += diff * 0.15;

    // --- Body bob (2x frequency) ---
    bodyRef.current.position.y =
      Math.sin(phase * BODY_BOB_FREQ * Math.PI * 2) * BODY_BOB_HEIGHT * wb;

    // --- Hip sway (0.5x frequency) ---
    const hipSway =
      Math.sin(phase * HIP_SWAY_FREQ * Math.PI * 2) * HIP_SWAY_AMPLITUDE * wb;

    // --- Torso counter-rotation + twist ---
    if (torsoRef.current) {
      torsoRef.current.rotation.z =
        -hipSway * (TORSO_COUNTER_ROT / HIP_SWAY_AMPLITUDE) * wb;
      torsoRef.current.rotation.y =
        Math.sin(phase * Math.PI * 2) * TORSO_TWIST * wb;
    }

    // --- Legs (opposite phase) ---
    const legSwing = Math.sin(phase * Math.PI * 2) * LEG_AMPLITUDE * wb;
    if (leftLegRef.current) leftLegRef.current.rotation.x = legSwing;
    if (rightLegRef.current) rightLegRef.current.rotation.x = -legSwing;

    // --- Arms (opposite to legs) ---
    const armSwing = Math.sin(phase * Math.PI * 2) * ARM_AMPLITUDE * wb;
    if (leftArmRef.current) leftArmRef.current.rotation.x = -armSwing;
    if (rightArmRef.current) rightArmRef.current.rotation.x = armSwing;

    // --- Head bob ---
    if (headRef.current) {
      headRef.current.position.y =
        1.2 + Math.sin(phase * BODY_BOB_FREQ * Math.PI * 2) * HEAD_BOB * wb;
    }

    // --- Idle (breathing sway) ---
    if (wb < 0.1) {
      bodyRef.current.rotation.z = Math.sin(t * IDLE_SWAY_FREQ) * IDLE_SWAY_AMP;
      bodyRef.current.position.y = Math.sin(t * IDLE_BREATHE_FREQ) * IDLE_BREATHE_AMP;
    }
  });

  return (
    <group ref={groupRef}>
      <group ref={bodyRef} scale={0.8}>
        {/* Legs pivot at hip Y=0.45 */}
        <group ref={leftLegRef} position={[-0.1, 0.45, 0]}>
          {/* leg mesh + foot mesh */}
        </group>
        <group ref={rightLegRef} position={[0.1, 0.45, 0]}>
          {/* leg mesh + foot mesh */}
        </group>

        {/* Torso group (counter-rotation applied here) */}
        <group ref={torsoRef}>
          {/* torso mesh at Y=0.72 */}
          {/* shoulders at Y=0.9 */}

          {/* Arms pivot at shoulders */}
          <group ref={leftArmRef} position={[-0.22, 0.9, 0]}>
            {/* arm mesh + hand mesh */}
          </group>
          <group ref={rightArmRef} position={[0.22, 0.9, 0]}>
            {/* arm mesh + hand mesh */}
          </group>

          {/* Head with bob ref */}
          <mesh ref={headRef} position={[0, 1.2, 0]}>
            {/* head geometry */}
          </mesh>
        </group>
      </group>
    </group>
  );
}
```

### Hierarchy Structure (critical for correct animation)

```
group (position lerp)
  └── body (rotation Y = facing direction, position Y = body bob)
      ├── leftLeg (rotation X = walk swing)
      │   ├── leg cylinder
      │   └── foot box
      ├── rightLeg (rotation X = -walk swing)
      │   ├── leg cylinder
      │   └── foot box
      └── torso (rotation Z = counter-rot, rotation Y = twist)
          ├── torso cylinder
          ├── shoulders
          ├── leftArm (rotation X = -arm swing)
          │   ├── arm cylinder
          │   └── hand sphere
          ├── rightArm (rotation X = arm swing)
          │   ├── arm cylinder
          │   └── hand sphere
          ├── head (position Y = base + head bob)
          ├── eyes
          └── hair
```

### Tuning Tips

- **Too fast?** Reduce `WALK_FREQ` (5.5 → 4.0 for slow walk)
- **Too robotic?** Increase `BODY_BOB_HEIGHT` and `HIP_SWAY_AMPLITUDE`
- **Too exaggerated?** Reduce `LEG_AMPLITUDE` and `ARM_AMPLITUDE`
- **Snapping between idle/walk?** Reduce smoothDamp speed (0.1 → 0.05)
- **For running**: Increase `WALK_FREQ` to 8-10, `LEG_AMPLITUDE` to 0.7, `BODY_BOB_HEIGHT` to 0.06

## Procedural Jump Animation (Point-to-Point)

Smooth jump between two 3D positions with squash & stretch. No physics engine needed.

### Key Principles

1. **3 phases**: Prepare (squash down) → Fly (parabolic arc) → Land (squash on impact)
2. **Y arc**: `sin(t * PI) * height` — natural parabola, 0 at both ends, peak at midpoint
3. **XZ movement**: ease-in-out cubic — starts slow, fast in middle, slow at end
4. **Squash & stretch**: compress body before jump, elongate in air, compress on landing

### Reference Values

| Parameter | Value | Purpose |
|-----------|-------|---------|
| Prepare duration | 0.15s | Anticipation squash |
| Fly duration | 0.6s | Arc through air |
| Land duration | 0.2s | Impact absorption |
| Jump height | 1.5-2.0 units | Peak of arc |
| Prepare squashY | 0.7 | Body compresses |
| Prepare stretchXZ | 1.15 | Body widens |
| Flight stretchY | 1.15 | Body elongates in air |
| Landing squashY | 0.75 | Impact compression |

### Implementation

```tsx
const JUMP_HEIGHT = 1.8;
const PREPARE_DURATION = 0.15;
const FLY_DURATION = 0.6;
const LAND_DURATION = 0.2;

type JumpPhase = 'idle' | 'prepare' | 'fly' | 'land';

function easeInOutCubic(t: number): number {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

// In useFrame:
if (phase === 'prepare') {
  const t = Math.min(1, timer / PREPARE_DURATION);
  const squash = 1 - 0.3 * Math.sin(t * Math.PI / 2);
  const stretch = 1 + 0.15 * Math.sin(t * Math.PI / 2);
  body.scale.set(stretch, squash, stretch);
  // Stay at start position
}

if (phase === 'fly') {
  const t = Math.min(1, timer / FLY_DURATION);
  // XZ: ease-in-out
  const eased = easeInOutCubic(t);
  const x = startX + (endX - startX) * eased;
  const z = startZ + (endZ - startZ) * eased;
  // Y: sin arc
  const baseY = startY + (endY - startY) * eased;
  const arcY = Math.sin(t * Math.PI) * JUMP_HEIGHT;
  group.position.set(x, baseY + arcY, z);

  // Squash/stretch during flight
  if (t < 0.3) body.scale.set(0.9, 1.15, 0.9);      // rising: stretch
  else if (t < 0.7) body.scale.set(1, 1, 1);          // peak: normal
  else body.scale.set(0.92, 1.1, 0.92);               // falling: slight stretch
}

if (phase === 'land') {
  const t = Math.min(1, timer / LAND_DURATION);
  group.position.copy(endPos);
  if (t < 0.4) {
    // Impact squash
    body.scale.set(1.12, 0.75, 1.12);
  } else {
    // Recover to normal
    const r = (t - 0.4) / 0.6;
    body.scale.set(1.12 - 0.12 * r, 0.75 + 0.25 * r, 1.12 - 0.12 * r);
  }
}
```

### Tuning Tips

- **Floaty jump?** Reduce `FLY_DURATION` (0.6 → 0.4) or `JUMP_HEIGHT`
- **Too snappy?** Increase `PREPARE_DURATION` (0.15 → 0.25)
- **No weight?** Increase squash values (0.7 → 0.6) for more compression
- **Board game hop**: Use shorter `JUMP_HEIGHT` (1.0) and faster `FLY_DURATION` (0.4)
- **Long distance**: Increase `JUMP_HEIGHT` proportionally to XZ distance

## See Also

- `r3f-loaders` - Loading animated GLTF models
- `r3f-fundamentals` - useFrame and animation loop
- `r3f-shaders` - Vertex animation in shaders
