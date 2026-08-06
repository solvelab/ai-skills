# Reference — Models: useGLTF (Drei)

Part of the `r3f-assets` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

## Models

### Quick Start

```tsx
import { Canvas } from '@react-three/fiber'
import { useGLTF, OrbitControls } from '@react-three/drei'
import { Suspense } from 'react'

function Model() {
  const { scene } = useGLTF('/models/robot.glb')
  return <primitive object={scene} />
}

export default function App() {
  return (
    <Canvas>
      <ambientLight />
      <Suspense fallback={null}>
        <Model />
      </Suspense>
      <OrbitControls />
    </Canvas>
  )
}
```

### useGLTF (Drei)

The recommended way to load GLTF/GLB models.

#### Basic Usage

```tsx
import { useGLTF } from '@react-three/drei'

function Model() {
  const gltf = useGLTF('/models/robot.glb')

  // gltf contains:
  // - scene: THREE.Group (the main scene)
  // - nodes: Object of named meshes
  // - materials: Object of named materials
  // - animations: Array of AnimationClip

  return <primitive object={gltf.scene} />
}
```

#### Using Nodes and Materials

```tsx
function Model() {
  const { nodes, materials } = useGLTF('/models/robot.glb')

  return (
    <group>
      {/* Use specific meshes */}
      <mesh
        geometry={nodes.Body.geometry}
        material={materials.Metal}
        position={[0, 0, 0]}
      />
      <mesh
        geometry={nodes.Head.geometry}
        material={materials.Plastic}
        position={[0, 1, 0]}
      />
    </group>
  )
}
```

#### With TypeScript (gltfjsx)

Generate typed components using gltfjsx:

```bash
npx gltfjsx model.glb --types
```

```tsx
// Generated component
import { useGLTF } from '@react-three/drei'
import { GLTF } from 'three-stdlib'

type GLTFResult = GLTF & {
  nodes: {
    Body: THREE.Mesh
    Head: THREE.Mesh
  }
  materials: {
    Metal: THREE.MeshStandardMaterial
    Plastic: THREE.MeshStandardMaterial
  }
}

export function Model(props: JSX.IntrinsicElements['group']) {
  const { nodes, materials } = useGLTF('/model.glb') as GLTFResult

  return (
    <group {...props} dispose={null}>
      <mesh geometry={nodes.Body.geometry} material={materials.Metal} />
      <mesh geometry={nodes.Head.geometry} material={materials.Plastic} />
    </group>
  )
}

useGLTF.preload('/model.glb')
```

#### Draco Compression

```tsx
import { useGLTF } from '@react-three/drei'

function Model() {
  // Drei automatically handles Draco if the file is Draco-compressed
  const { scene } = useGLTF('/models/compressed.glb')
  return <primitive object={scene} />
}

// Or specify Draco decoder path
useGLTF.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.6/')
```

#### Preloading

```tsx
import { useGLTF } from '@react-three/drei'

// Preload at module level
useGLTF.preload('/models/robot.glb')
useGLTF.preload(['/model1.glb', '/model2.glb'])

function Model() {
  // Will be instant if preloaded
  const { scene } = useGLTF('/models/robot.glb')
  return <primitive object={scene} />
}
```

#### Processing Loaded Model

```tsx
function Model() {
  const { scene } = useGLTF('/models/robot.glb')

  useEffect(() => {
    // Enable shadows on all meshes
    scene.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true
        child.receiveShadow = true
      }
    })
  }, [scene])

  return <primitive object={scene} />
}
```

### useLoader for GLTF (Core R3F)

#### With Extensions (Draco)

```tsx
import { useLoader } from '@react-three/fiber'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js'

function Model() {
  const gltf = useLoader(GLTFLoader, '/model.glb', (loader) => {
    const dracoLoader = new DRACOLoader()
    dracoLoader.setDecoderPath('https://www.gstatic.com/draco/v1/decoders/')
    loader.setDRACOLoader(dracoLoader)
  })

  return <primitive object={gltf.scene} />
}
```

#### Progress Callback

```tsx
function Model() {
  const gltf = useLoader(
    GLTFLoader,
    '/model.glb',
    undefined,  // extensions
    (progress) => {
      console.log(`Loading: ${(progress.loaded / progress.total) * 100}%`)
    }
  )

  return <primitive object={gltf.scene} />
}
```

