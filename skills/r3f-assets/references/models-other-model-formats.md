# Reference — Models: Other Model Formats

Part of the `r3f-assets` skill. Conventions, version pin and topic index: [../SKILL.md](../SKILL.md).

---

### Other Model Formats

#### OBJ + MTL

```tsx
import { useLoader } from '@react-three/fiber'
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js'
import { MTLLoader } from 'three/addons/loaders/MTLLoader.js'

function OBJModel() {
  const materials = useLoader(MTLLoader, '/model.mtl')
  const obj = useLoader(OBJLoader, '/model.obj', (loader) => {
    materials.preload()
    loader.setMaterials(materials)
  })

  return <primitive object={obj} />
}
```

#### FBX

```tsx
import { useFBX } from '@react-three/drei'

function FBXModel() {
  const fbx = useFBX('/model.fbx')

  return <primitive object={fbx} scale={0.01} />
}

// Preload
useFBX.preload('/model.fbx')
```

#### STL

```tsx
import { useLoader } from '@react-three/fiber'
import { STLLoader } from 'three/addons/loaders/STLLoader.js'

function STLModel() {
  const geometry = useLoader(STLLoader, '/model.stl')

  return (
    <mesh geometry={geometry}>
      <meshStandardMaterial color="gray" />
    </mesh>
  )
}
```

#### PLY

```tsx
import { useLoader } from '@react-three/fiber'
import { PLYLoader } from 'three/addons/loaders/PLYLoader.js'

function PLYModel() {
  const geometry = useLoader(PLYLoader, '/model.ply')

  useEffect(() => {
    geometry.computeVertexNormals()
  }, [geometry])

  return (
    <mesh geometry={geometry}>
      <meshStandardMaterial vertexColors />
    </mesh>
  )
}
```

### Clone for Multiple Instances

```tsx
import { useGLTF, Clone } from '@react-three/drei'

function Trees() {
  const { scene } = useGLTF('/models/tree.glb')

  return (
    <>
      <Clone object={scene} position={[0, 0, 0]} />
      <Clone object={scene} position={[5, 0, 0]} />
      <Clone object={scene} position={[-5, 0, 0]} />
      <Clone object={scene} position={[0, 0, 5]} scale={1.5} />
    </>
  )
}
```

### useFont

```tsx
import { useFont, Text3D } from '@react-three/drei'

// Preload font
useFont.preload('/fonts/helvetiker.json')

function Text() {
  return (
    <Text3D font="/fonts/helvetiker.json" size={1} height={0.2}>
      Hello
      <meshStandardMaterial color="gold" />
    </Text3D>
  )
}
```

### Error Handling

```tsx
import { useGLTF } from '@react-three/drei'
import { ErrorBoundary } from 'react-error-boundary'

function ModelWithErrorHandling() {
  return (
    <ErrorBoundary fallback={<FallbackModel />}>
      <Suspense fallback={<Loader />}>
        <Model />
      </Suspense>
    </ErrorBoundary>
  )
}

function FallbackModel() {
  return (
    <mesh>
      <boxGeometry />
      <meshBasicMaterial color="red" wireframe />
    </mesh>
  )
}
```

### Asset Caching

```tsx
import { useGLTF, useTexture } from '@react-three/drei'

// Assets are automatically cached by URL
// Same URL = same asset instance

function Scene() {
  // These all reference the same cached asset
  const model1 = useGLTF('/model.glb')
  const model2 = useGLTF('/model.glb')
  const model3 = useGLTF('/model.glb')

  // Clear cache if needed
  useGLTF.clear('/model.glb')
}
```

