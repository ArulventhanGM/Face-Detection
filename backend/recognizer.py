import face_recognition
import cv2
import os
import numpy as np
import pickle

KNOWN_FACES_DIR = "../known_faces"
ENCODINGS_FILE = "encodings.pkl"
OUTPUT_DIR = "../outputs"

def load_known_faces():
    """
    Load known faces from the known_faces directory and cache encodings.
    
    Returns:
        tuple: (known_face_encodings, known_face_names)
    """
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if os.path.exists(ENCODINGS_FILE):
        print("Loading cached face encodings...")
        with open(ENCODINGS_FILE, 'rb') as f:
            known_face_encodings, known_face_names = pickle.load(f)
    else:
        print("Creating new face encodings...")
        known_face_encodings = []
        known_face_names = []
        
        if not os.path.exists(KNOWN_FACES_DIR):
            print(f"Warning: {KNOWN_FACES_DIR} directory not found. Creating it...")
            os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
            return known_face_encodings, known_face_names
        
        for filename in os.listdir(KNOWN_FACES_DIR):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(KNOWN_FACES_DIR, filename)
                print(f"Processing {filename}...")
                
                try:
                    image = face_recognition.load_image_file(image_path)
                    encodings = face_recognition.face_encodings(image)
                    
                    if encodings:
                        known_face_encodings.append(encodings[0])
                        name = os.path.splitext(filename)[0]
                        known_face_names.append(name)
                        print(f"  ✓ Added {name}")
                    else:
                        print(f"  ✗ No face found in {filename}")
                except Exception as e:
                    print(f"  ✗ Error processing {filename}: {e}")

        # Save encodings to avoid reprocessing
        if known_face_encodings:
            with open(ENCODINGS_FILE, 'wb') as f:
                pickle.dump((known_face_encodings, known_face_names), f)
            print(f"Cached {len(known_face_encodings)} face encodings")

    return known_face_encodings, known_face_names

def recognize_faces_in_image(image_path, tolerance=0.5):
    """
    Recognize faces in a group image and return annotated results.
    
    Args:
        image_path (str): Path to the group image
        tolerance (float): Face matching tolerance (lower is more strict)
        
    Returns:
        tuple: (recognized_names, output_path)
    """
    # Load known faces
    known_face_encodings, known_face_names = load_known_faces()
    
    if not known_face_encodings:
        print("No known faces loaded. Please add images to the known_faces directory.")
        return [], None

    try:
        # Load group image
        image = face_recognition.load_image_file(image_path)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Detect faces
        print("Detecting faces in the uploaded image...")
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        print(f"Found {len(face_locations)} face(s) in the image")

        recognized_names = []

        for i, ((top, right, bottom, left), face_encoding) in enumerate(zip(face_locations, face_encodings)):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=tolerance)
            name = "Unknown"

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            if face_distances.size > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index] and face_distances[best_match_index] < tolerance:
                    name = known_face_names[best_match_index]
                    print(f"  Face {i+1}: Recognized as {name} (distance: {face_distances[best_match_index]:.3f})")
                else:
                    print(f"  Face {i+1}: Unknown (best distance: {face_distances[best_match_index]:.3f})")

            recognized_names.append(name)

            # Draw box and name
            cv2.rectangle(rgb_image, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(rgb_image, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            
            # Use a smaller font if name is long
            font_scale = 0.8 if len(name) > 10 else 1.0
            cv2.putText(rgb_image, name, (left + 6, bottom - 6), 
                       cv2.FONT_HERSHEY_DUPLEX, font_scale, (255, 255, 255), 1)

        # Save the annotated image
        output_filename = f"{os.path.splitext(os.path.basename(image_path))[0]}_annotated.jpg"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        cv2.imwrite(output_path, rgb_image)
        
        print(f"Annotated image saved to: {output_path}")
        return recognized_names, output_path

    except Exception as e:
        print(f"Error processing image: {e}")
        return [], None

def refresh_encodings():
    """
    Force refresh of face encodings by deleting the cache file.
    """
    if os.path.exists(ENCODINGS_FILE):
        os.remove(ENCODINGS_FILE)
        print("Face encodings cache cleared. Will rebuild on next recognition.")

def get_known_faces_info():
    """
    Get information about known faces.
    
    Returns:
        dict: Information about loaded faces
    """
    known_face_encodings, known_face_names = load_known_faces()
    
    return {
        "total_faces": len(known_face_names),
        "known_names": known_face_names,
        "encodings_cached": os.path.exists(ENCODINGS_FILE)
    }

if __name__ == "__main__":
    # Test the face recognition system
    print("=== Face Recognition Test ===")
    info = get_known_faces_info()
    print(f"Known faces: {info['total_faces']}")
    print(f"Names: {info['known_names']}")
    
    # Test with a sample image if available
    test_image = "../test_images/group_photo.jpg"
    if os.path.exists(test_image):
        print(f"\nTesting with {test_image}...")
        names, output = recognize_faces_in_image(test_image)
        print(f"Recognized: {names}")
        print(f"Output saved to: {output}")
    else:
        print(f"\nNo test image found at {test_image}")
