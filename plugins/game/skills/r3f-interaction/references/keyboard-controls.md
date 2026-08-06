# Reference — Keyboard Controls

Part of the `r3f-interaction` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Transform Controls

Gizmo for moving/rotating/scaling objects.

```tsx
import { TransformControls, OrbitControls } from '@react-three/drei'
import { useRef, useState } from 'react'

function Scene() {
  const meshRef = useRef<THREE.Mesh>(null!)
  const [mode, setMode] = useState('translate')
  const orbitRef = useRef<React.ComponentRef<typeof OrbitControls>>(null!)

  return (
    <>
      <OrbitControls ref={orbitRef} makeDefault />

      <TransformControls
        object={meshRef}
        mode={mode}  // 'translate' | 'rotate' | 'scale'
        space="local"  // 'local' | 'world'
        onMouseDown={() => {
          // Disable orbit while transforming
          if (orbitRef.current) orbitRef.current.enabled = false
        }}
        onMouseUp={() => {
          if (orbitRef.current) orbitRef.current.enabled = true
        }}
      />

      <mesh ref={meshRef}>
        <boxGeometry />
        <meshStandardMaterial color="orange" />
      </mesh>

      {/* Mode switching buttons in HTML */}
      <div className="controls">
        <button onClick={() => setMode('translate')}>Move</button>
        <button onClick={() => setMode('rotate')}>Rotate</button>
        <button onClick={() => setMode('scale')}>Scale</button>
      </div>
    </>
  )
}
```

### PivotControls

Alternative transform gizmo with pivot point.

```tsx
import { PivotControls } from '@react-three/drei'

function Scene() {
  return (
    <PivotControls
      anchor={[0, 0, 0]}         // Anchor point
      depthTest={false}          // Always visible
      lineWidth={2}              // Axis line width
      axisColors={['red', 'green', 'blue']}
      scale={1}                  // Gizmo scale
      fixed={false}              // Fixed screen size
    >
      <mesh>
        <boxGeometry />
        <meshStandardMaterial color="orange" />
      </mesh>
    </PivotControls>
  )
}
```

## Drag Controls

### useDrag from @use-gesture/react

```bash
npm install @use-gesture/react
```

```tsx
import { useDrag } from '@use-gesture/react'
import { useSpring, animated } from '@react-spring/three'
import { useThree } from '@react-three/fiber'

function DraggableMesh() {
  const { size, viewport } = useThree()
  const aspect = size.width / viewport.width

  const [spring, api] = useSpring(() => ({
    position: [0, 0, 0],
    config: { mass: 1, tension: 280, friction: 60 }
  }))

  const bind = useDrag(({ movement: [mx, my], down }) => {
    api.start({
      position: down ? [mx / aspect, -my / aspect, 0] : [0, 0, 0]
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

### DragControls (Drei)

```tsx
import { DragControls, OrbitControls } from '@react-three/drei'
import { useRef } from 'react'

function Scene() {
  const meshRef = useRef<THREE.Mesh>(null!)
  const orbitRef = useRef<React.ComponentRef<typeof OrbitControls>>(null!)

  return (
    <>
      <OrbitControls ref={orbitRef} makeDefault />

      <DragControls
        onDragStart={() => {
          if (orbitRef.current) orbitRef.current.enabled = false
        }}
        onDragEnd={() => {
          if (orbitRef.current) orbitRef.current.enabled = true
        }}
      >
        <mesh ref={meshRef}>
          <boxGeometry />
          <meshStandardMaterial color="orange" />
        </mesh>
      </DragControls>
    </>
  )
}
```

## Keyboard Controls

### KeyboardControls (Drei)

```tsx
import { KeyboardControls, useKeyboardControls } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'

// Define key mappings
const keyMap = [
  { name: 'forward', keys: ['ArrowUp', 'KeyW'] },
  { name: 'backward', keys: ['ArrowDown', 'KeyS'] },
  { name: 'left', keys: ['ArrowLeft', 'KeyA'] },
  { name: 'right', keys: ['ArrowRight', 'KeyD'] },
  { name: 'jump', keys: ['Space'] },
  { name: 'sprint', keys: ['ShiftLeft'] },
]

function Player() {
  const meshRef = useRef<THREE.Mesh>(null!)
  const [, getKeys] = useKeyboardControls()

  useFrame((state, delta) => {
    const { forward, backward, left, right, jump, sprint } = getKeys()

    const speed = sprint ? 10 : 5

    if (forward) meshRef.current.position.z -= speed * delta
    if (backward) meshRef.current.position.z += speed * delta
    if (left) meshRef.current.position.x -= speed * delta
    if (right) meshRef.current.position.x += speed * delta
    if (jump) meshRef.current.position.y += speed * delta
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="blue" />
    </mesh>
  )
}

export default function App() {
  return (
    <KeyboardControls map={keyMap}>
      <Canvas>
        <ambientLight />
        <Player />
      </Canvas>
    </KeyboardControls>
  )
}
```

### Subscribe to Key Changes

```tsx
import { useKeyboardControls } from '@react-three/drei'
import { useEffect } from 'react'

function KeyListener() {
  const jumpPressed = useKeyboardControls((state) => state.jump)

  useEffect(() => {
    if (jumpPressed) {
      console.log('Jump!')
    }
  }, [jumpPressed])

  return null
}
```

