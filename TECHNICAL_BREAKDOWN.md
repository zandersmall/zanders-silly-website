# Website Technical Breakdown - Portfolio/Personal Website

## 🎯 Overview

This is a **3D interactive portfolio website** that combines traditional web content with an immersive Three.js 3D room environment. The site features smooth scroll-triggered animations, theme switching, and a sophisticated preloading system.

---

## 📦 Tech Stack & Packages

### Core Technologies

#### **Build Tool & Development**
- **Vite 3.1.0** - Modern build tool and dev server
  - Fast HMR (Hot Module Replacement)
  - ES modules based bundling
  - Optimized production builds
  - Used for: Development server (`npm run dev`), production builds, and asset optimization

#### **3D Graphics & WebGL**
- **Three.js 0.141.0** - Primary 3D rendering library
  - WebGL renderer for browser-based 3D graphics
  - Scene graph management
  - Camera systems (Perspective & Orthographic)
  - Geometry, materials, lights, shadows
  - GLTF model loading
  - Animation mixer for model animations
  - Used for: Entire 3D room scene, camera movement, model rendering

#### **Animation & UI**
- **GSAP (GreenSock) 3.10.4** - High-performance animation library
  - Timeline-based animations
  - ScrollTrigger plugin for scroll-based animations
  - Smooth easing functions
  - Used for: Preloader animations, scroll-triggered camera/room movement, text animations, theme transitions

- **ASScroll (@ashthornton/asscroll) 2.0.7** - Custom smooth scroll library
  - Smooth scrolling implementation
  - Integrated with GSAP ScrollTrigger
  - Used for: Desktop smooth scrolling experience

#### **User Interface**
- **lil-gui 0.16.1** - Lightweight debugging GUI (currently commented out in production)
  - Used for: Development/testing controls (light color, intensity debugging)

#### **Event System**
- **events 3.3.0** - Node.js events polyfill for browser
  - Used for: Custom event emitter pattern throughout the application

#### **Analytics**
- **@vercel/analytics 0.1.7** - Vercel Analytics integration
  - Used for: Website analytics and performance monitoring

---

## 🏗️ Architecture & Design Patterns

### **1. Singleton Pattern**
The `Experience` class uses a singleton pattern to ensure only one instance exists:
```16:22:Experience/Experience.js
export default class Experience {
    static instance;
    constructor(canvas) {
        if (Experience.instance) {
            return Experience.instance;
        }
        Experience.instance = this;
```

### **2. Event-Driven Architecture**
Multiple classes extend `EventEmitter` to facilitate decoupled communication:
- `Time` - Emits 'update' on every frame
- `Sizes` - Emits 'resize' on window resize, 'switchdevice' on device change
- `Resources` - Emits 'ready' when all assets loaded
- `Theme` - Emits 'switch' on theme toggle
- `World` - Emits 'worldready' when 3D scene is initialized
- `Preloader` - Emits 'enablecontrols' when preloader sequence completes

### **3. Modular Component Structure**
```
Experience/
├── Experience.js        # Main singleton orchestrator
├── Camera.js            # Dual camera setup (Perspective + Orthographic)
├── Renderer.js          # WebGL renderer configuration
├── Preloader.js         # Loading screen & intro animations
├── Theme.js             # Light/dark theme system
├── Utils/
│   ├── Sizes.js         # Window size tracking & device detection
│   ├── Time.js          # Frame timing & delta calculation
│   ├── Resources.js     # Asset loading manager
│   └── assets.js        # Asset manifest
└── World/
    ├── World.js         # 3D scene coordinator
    ├── Room.js          # 3D room model management
    ├── Floor.js         # Floor plane & decorative circles
    ├── Environment.js   # Lighting setup
    └── Controls.js      # Scroll-based camera & room animations
```

---

## 🔄 Application Flow

### **Initialization Sequence**

1. **HTML Loads** (`index.html`)
   - Canvas element created: `<canvas class="experience-canvas"></canvas>`
   - Preloader UI rendered
   - Page content sections structured with `asscroll-container` and `asscroll` attributes

2. **JavaScript Entry Point** (`main.js`)
   ```1:4:main.js
   import "./style.css";
   import Experience from "./Experience/Experience.js";
   
   const experience = new Experience(document.querySelector(".experience-canvas"));
   ```

3. **Experience Singleton Creation** (`Experience.js`)
   - Creates Three.js scene
   - Initializes utility classes: `Time`, `Sizes`, `Resources`
   - Sets up `Camera`, `Renderer`, `Theme`, `Preloader`
   - Creates `World` instance
   - Registers resize and update event listeners

4. **Resource Loading** (`Resources.js`)
   - Loads GLTF room model (`Zander Room.glb`) with DRACO compression
   - Loads video texture for computer screen (`coding2.mp4`)
   - Emits 'ready' when all assets loaded

5. **World Initialization** (`World.js`)
   - Waits for resources 'ready' event
   - Creates `Environment` (lights), `Floor`, `Room`
   - Emits 'worldready' event

6. **Preloader Sequence** (`Preloader.js`)
   - Waits for 'worldready' event
   - Converts text elements to span-wrapped characters for animation
   - Executes two-part intro animation:
     - **First Intro**: Preloader fade, room cube animation, intro text reveal
     - **User Scroll**: Waits for scroll/touch gesture
     - **Second Intro**: Room transformation, hero text reveal, room objects animate in
   - Emits 'enablecontrols' when complete

7. **Controls Activation** (`Controls.js`)
   - Activated after preloader completes
   - Sets up ASScroll for smooth scrolling (desktop only)
   - Registers GSAP ScrollTrigger animations for scroll-based 3D movements
   - Configures section-based animations (progress bars, room position, camera movement)

### **Runtime Loop**

Every frame (via `requestAnimationFrame`):
```
Time.update() 
  → emits 'update' 
    → Experience.update()
      → Preloader.update()
      → Camera.update()
      → World.update()
        → Room.update() (mouse rotation, animations)
      → Renderer.update() (renders scene to canvas)
      → Controls.update() (if enabled)
```

### **User Interactions**

**Theme Toggle:**
- User clicks toggle button → `Theme.js` handles click
- Updates DOM classes → Emits 'switch' event
- `Environment.js` listens and animates light colors with GSAP

**Scrolling:**
- User scrolls → ASScroll (desktop) or native scroll (mobile)
- ScrollTrigger detects scroll position
- Animates:
  - Room position/scale/rotation
  - Camera position
  - Floor circles scale
  - Section border radius
  - Progress bars

**Mouse Movement:**
- `Room.js` listens to mousemove events
- Calculates rotation based on mouse X position
- Smoothly interpolates room rotation using GSAP utils

---

## 🎨 Key Features & Implementation Details

### **1. Dual Camera System**

The application uses two cameras simultaneously:
- **Orthographic Camera** (Primary) - For the main 3D view (no perspective distortion)
- **Perspective Camera** (Secondary) - Currently used only for OrbitControls, not rendered

```30:45:Experience/Camera.js
createOrthographicCamera() {
    this.orthographicCamera = new THREE.OrthographicCamera(
        (-this.sizes.aspect * this.sizes.frustrum) / 2,
        (this.sizes.aspect * this.sizes.frustrum) / 2,
        this.sizes.frustrum / 2,
        -this.sizes.frustrum / 2,
        -50,
        50
    );

    // 6.5
    this.orthographicCamera.position.y = 5.65;
    this.orthographicCamera.position.z = 10;
    this.orthographicCamera.rotation.x = -Math.PI / 6;
```

### **2. Asset Loading with DRACO Compression**

GLTF models are loaded with DRACO geometry compression for smaller file sizes:
```24:29:Experience/Utils/Resources.js
setLoaders() {
    this.loaders = {};
    this.loaders.gltfLoader = new GLTFLoader();
    this.loaders.dracoLoader = new DRACOLoader();
    this.loaders.dracoLoader.setDecoderPath("/draco/");
    this.loaders.gltfLoader.setDRACOLoader(this.loaders.dracoLoader);
```

### **3. Video Texture on 3D Model**

A video file is used as a texture for the computer screen mesh:
```37:58:Experience/Utils/Resources.js
} else if (asset.type === "videoTexture") {
    this.video = {};
    this.videoTexture = {};

    this.video[asset.name] = document.createElement("video");
    this.video[asset.name].src = asset.path;
    this.video[asset.name].muted = true;
    this.video[asset.name].playsInline = true;
    this.video[asset.name].autoplay = true;
    this.video[asset.name].loop = true;
    this.video[asset.name].play();

    this.videoTexture[asset.name] = new THREE.VideoTexture(
        this.video[asset.name]
    );
    // this.videoTexture[asset.name].flipY = false;
    this.videoTexture[asset.name].minFilter = THREE.NearestFilter;
    this.videoTexture[asset.name].magFilter = THREE.NearestFilter;
    this.videoTexture[asset.name].generateMipmaps = false;
    this.videoTexture[asset.name].encoding = THREE.sRGBEncoding;
```

Applied to the Computer mesh:
```51:55:Experience/World/Room.js
if (child.name === "Computer") {
    child.children[1].material = new THREE.MeshBasicMaterial({
        map: this.resources.items.screen,
    });
}
```

### **4. Advanced Material - Glass Effect (Aquarium)**

Uses `MeshPhysicalMaterial` with transmission for realistic glass:
```41:49:Experience/World/Room.js
if (child.name === "Aquarium") {
    // console.log(child);
    child.children[0].material = new THREE.MeshPhysicalMaterial();
    child.children[0].material.roughness = 0;
    child.children[0].material.color.set(0x549dd2);
    child.children[0].material.ior = 3;
    child.children[0].material.transmission = 1;
    child.children[0].material.opacity = 1;
}
```

### **5. Scroll-Triggered Animations**

Multiple GSAP timelines sync with scroll position:
- Room position/scale changes per section
- Camera movements
- Light adjustments
- Floor circle scaling
- Section border radius animations
- Progress bar fills

Example for first section:
```100:118:Experience/World/Controls.js
this.firstMoveTimeline = new GSAP.timeline({
    scrollTrigger: {
        trigger: ".first-move",
        start: "top top",
        end: "bottom bottom",
        scrub: 0.6,
        // markers: true,
        invalidateOnRefresh: true,
    },
});
this.firstMoveTimeline.fromTo(
    this.room.position,
    { x: 0, y: 0, z: 0 },
    {
        x: () => {
            return this.sizes.width * 0.0014;
        },
    }
);
```

### **6. Responsive Design**

- Device detection: `< 968px` = mobile, `>= 968px` = desktop
- Different room scales: `0.11` (desktop) vs `0.07` (mobile)
- Different camera positions and animations per device
- Smooth scrolling disabled on mobile (native scroll used)

### **7. Performance Optimizations**

- **Shadow Maps**: PCFSoftShadowMap for soft shadows
- **Pixel Ratio**: Capped at 2 to prevent over-rendering on high-DPI displays
- **Tone Mapping**: CineonToneMapping with exposure control
- **Lerping**: Mouse rotation uses interpolation for smooth movement
- **Animation Mixer**: Efficiently handles model animations

---

## 🔐 Security & Best Practices

### **Current Security Considerations:**

1. **Content Security**: No external API calls or user input processing
2. **Asset Loading**: All assets served from same domain
3. **Video Autoplay**: Videos muted (required for autoplay policies)
4. **No Authentication**: Static portfolio site, no sensitive data

### **Scalability Considerations:**

**Current State:**
- Single GLTF model loaded (~likely 10-100MB compressed)
- Single video texture (~few MB)
- No asset lazy loading
- No code splitting

**Potential Improvements for Scale:**
1. **Lazy Loading**: Load sections only when scrolled into view
2. **Code Splitting**: Split 3D rendering code from static content
3. **Model Optimization**: Further compress/optimize 3D models
4. **Asset CDN**: Serve large assets from CDN with compression
5. **Progressive Loading**: Show low-poly placeholder while loading
6. **Web Workers**: Move asset processing to web workers
7. **Service Worker**: Cache assets for repeat visits

---

## 📊 Performance Characteristics

### **Rendering:**
- **Target FPS**: 60 FPS (via requestAnimationFrame)
- **Renderer**: WebGL 2.0 (with fallback)
- **Shadow Quality**: 2048x2048 shadow maps
- **Antialiasing**: Enabled on renderer

### **Memory Management:**
- No explicit cleanup needed for current scope
- Three.js handles WebGL context management
- Event listeners properly bound/removed in preloader

### **Bundle Size Considerations:**
- Three.js: ~600KB minified
- GSAP: ~45KB minified
- ASScroll: ~10KB minified
- Total JS: ~1-2MB before minification, ~500-800KB minified+gzipped
- 3D Model: Variable (GLTF with DRACO compression)
- Video: Variable (MP4 format)

---

## 🎓 Technical Interview Talking Points

### **Architecture Decisions:**

1. **Why Singleton for Experience?**
   - Ensures single source of truth for 3D scene
   - Prevents multiple WebGL contexts
   - Simplifies global access pattern

2. **Why Event-Driven?**
   - Decouples components (Resources doesn't know about World)
   - Makes testing easier (mock event emitters)
   - Allows multiple listeners per event

3. **Why Dual Camera?**
   - Orthographic for clean portfolio view (no perspective distortion)
   - Perspective available for future features/development
   - Different use cases require different camera types

4. **Why GSAP over CSS Animations?**
   - Better performance for 3D object animations
   - ScrollTrigger integration is superior
   - Timeline control for complex sequences
   - Can animate Three.js objects directly

### **Challenges Overcome:**

1. **Smooth Scrolling + ScrollTrigger Integration**
   - ASScroll custom scroller integrated with GSAP's ScrollTrigger
   - Required scrollerProxy to make them work together

2. **Mobile vs Desktop Animations**
   - Different timelines per device breakpoint
   - Responsive 3D positioning and scaling
   - Touch event handling alongside scroll

3. **Preloader Sequence**
   - Two-phase animation with user interaction gate
   - Synchronized DOM and 3D animations
   - Proper cleanup of event listeners

4. **Performance on Low-End Devices**
   - Pixel ratio capping
   - Shadow map size optimization
   - Lerping prevents janky mouse movement

### **Potential Improvements:**

1. **Asset Management**: Implement asset preloading strategy
2. **Error Handling**: Add error boundaries for failed asset loads
3. **Accessibility**: Add keyboard navigation, ARIA labels
4. **Testing**: Unit tests for utility classes, integration tests for animations
5. **Type Safety**: Migrate to TypeScript for better DX
6. **State Management**: Consider state management library if features grow

---

## 🚀 Deployment & Build

**Development:**
```bash
npm run dev        # Vite dev server with HMR
```

**Production Build:**
```bash
npm run build      # Vite production build (optimized, minified)
npm run preview    # Preview production build locally
```

**Deployment:**
- Currently appears to be deployed on Vercel (analytics integration)
- Static site, no server-side requirements
- Assets served from `/public` directory
- Draco decoder files must be accessible for GLTF loading

---

## 📝 Summary

This is a **sophisticated single-page portfolio website** that demonstrates:
- Advanced 3D web graphics (Three.js)
- Complex animation sequencing (GSAP)
- Event-driven architecture
- Responsive 3D experiences
- Performance optimization techniques
- Modern build tooling (Vite)

The codebase shows strong understanding of:
- Object-oriented JavaScript
- Design patterns (Singleton, Observer/Event Emitter)
- WebGL/3D graphics pipeline
- Animation principles
- Performance considerations
- User experience design

Perfect for discussing in technical interviews as it showcases both frontend engineering skills and creative technical problem-solving!



