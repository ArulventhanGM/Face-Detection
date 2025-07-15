# Known Faces Setup Guide

## 📸 Adding Test Images for Face Recognition

To fully test your face recognition application, you need to add individual photos of people to the `known_faces/` directory.

### 🎯 **Quick Setup for Testing**

#### **Step 1: Prepare Individual Photos**
You need clear, front-facing photos of individuals. Here's what works best:

**✅ Good Photos:**
- Clear, well-lit face photos
- Front-facing or slight angle
- Single person per image
- Good resolution (at least 300x300 pixels)
- Minimal shadows on face

**❌ Avoid:**
- Group photos (use individual crops instead)
- Sunglasses or face coverings
- Very dark or blurry photos
- Side profiles
- Multiple people in one image

#### **Step 2: File Naming Convention**
Save photos using this format: `firstname_lastname.jpg`

**Examples:**
- `john_doe.jpg` - Will match metadata for "John Doe"
- `jane_smith.jpg` - Will match metadata for "Jane Smith"
- `bob_johnson.jpg` - Will match metadata for "Bob Johnson"
- `alice_brown.jpg` - Will match metadata for "Alice Brown"
- `mike_wilson.jpg` - Will match metadata for "Mike Wilson"

#### **Step 3: Where to Get Test Images**

**Option A: Use Your Own Photos**
- Take photos of yourself, family, or friends
- Crop them to show just the face area
- Save with the naming convention above

**Option B: Use Sample Images**
- Download sample face images from free sources like:
  - Unsplash.com (search "portrait" or "headshot")
  - Pexels.com (search "business portrait")
  - Generated faces from thispersondoesnotexist.com

**Option C: Create Test Dataset**
I can help you create a simple test script to download some sample images.

### 🚀 **Quick Test Setup**

1. **Add at least 3-5 individual face photos** to `known_faces/` directory
2. **Name them properly**: `firstname_lastname.jpg`
3. **Update metadata** if needed in `backend/metadata_handler.py`
4. **Start the application**: `python launcher.py`
5. **Test with a group photo** containing some of the same people

### 📱 **Testing Workflow**

1. **Prepare Known Faces** (individual photos in `known_faces/`)
2. **Create Test Group Photo** (photo with multiple people, including some from known_faces)
3. **Upload Group Photo** via web interface
4. **View Results** to see face recognition in action

### 🔧 **Current Metadata Available**

The application already has metadata for these names:
- `john_doe` - John Doe, Software Engineer
- `jane_smith` - Jane Smith, Product Manager  
- `bob_johnson` - Bob Johnson, Senior Developer
- `alice_brown` - Alice Brown, UX Designer
- `mike_wilson` - Mike Wilson, Data Scientist

If you add photos with these exact names, they'll automatically show rich metadata!

### 📂 **Directory Structure After Setup**
```
known_faces/
├── john_doe.jpg          # Individual photo of John
├── jane_smith.jpg        # Individual photo of Jane
├── bob_johnson.jpg       # Individual photo of Bob
├── alice_brown.jpg       # Individual photo of Alice
└── mike_wilson.jpg       # Individual photo of Mike
```

### 🎯 **Next Steps**

1. **Add your test images** to `known_faces/` directory
2. **Run the application**: `python launcher.py`
3. **Upload a group photo** for testing
4. **See the magic happen** - faces will be detected and labeled!

### 💡 **Pro Tips**

- Start with 3-5 known faces for initial testing
- Use high-quality, well-lit photos for better recognition
- Test with group photos that include both known and unknown people
- Adjust tolerance settings (0.3-1.0) for different accuracy levels
- The demo mode works without actual face recognition - install full dependencies for real AI processing

### 🔄 **After Adding Images**

Remember to refresh the face encodings cache:
- Via web interface: Click "Refresh Database" button
- Via API: `POST /api/refresh-encodings`
- Or restart the application

---

**Ready to test your face recognition system!** 🎭
