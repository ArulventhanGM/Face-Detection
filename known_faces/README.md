# Sample Known Faces Directory

This directory should contain individual photos of people you want to recognize.

## File Naming Convention
- Use format: `firstname_lastname.jpg`
- Examples: `john_doe.jpg`, `jane_smith.jpg`, `bob_johnson.jpg`

## Photo Requirements
- Clear, front-facing photos
- Good lighting
- One person per photo
- Supported formats: JPG, JPEG, PNG
- Recommended size: 500x500 pixels or higher

## Sample Files to Add

To test the application, add photos with these names:
- `john_doe.jpg` - Will match metadata for John Doe
- `jane_smith.jpg` - Will match metadata for Jane Smith
- `bob_johnson.jpg` - Will match metadata for Bob Johnson
- `alice_brown.jpg` - Will match metadata for Alice Brown
- `mike_wilson.jpg` - Will match metadata for Mike Wilson

## Adding New People

1. Add their photo to this directory
2. Update the metadata in `backend/metadata_handler.py`
3. Refresh the face encodings cache via the web interface or API

## Performance Tips

- Use consistent lighting across all photos
- Avoid sunglasses or face coverings
- Center the face in the image
- Use high-quality images for better recognition accuracy
