# Beautiful Calculator

A modern, visually appealing calculator application with both frontend and backend components. The calculator features a gradient design, smooth animations, keyboard support, and a robust backend API for calculations.

## Features

- **Beautiful Design**: Modern gradient background with glassmorphism effects
- **Responsive Layout**: Works seamlessly on desktop and mobile devices
- **Keyboard Support**: Full keyboard input support for all operations
- **Backend API**: FastAPI-powered backend for reliable calculations
- **Error Handling**: Comprehensive error handling for invalid operations
- **Smooth Animations**: Hover effects and transitions for enhanced UX

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install fastapi uvicorn
   ```

2. **Run Backend**
   ```bash
   uvicorn backend:app --reload --port 8000
   ```

3. **Open Frontend**
   Open `index.html` in your browser or serve it via any HTTP server.

## Backend API

### Endpoint: `POST /calculate`

**Request Body:**
```json
{
  "num1": 10,
  "num2": 5,
  "operation": "+"
}
```

**Supported Operations:**
- Addition: `+`
- Subtraction: `-`
- Multiplication: `*`
- Division: `/`

**Response:**
```json
{
  "result": 15
}
```

## Testing

Run the comprehensive test suite:
```bash
pytest test_app.py -v
```

Tests cover:
- Valid arithmetic operations
- Division by zero handling
- Invalid operation detection
- Negative numbers
- Large numbers
- Input validation
- CORS headers
- Floating-point precision

## Project Structure

```
output/
├── backend.py      # FastAPI backend
├── index.html     # Frontend calculator
├── test_app.py    # Comprehensive tests
└── readme.md      # This file
```

## Usage

1. Enter numbers using the on-screen buttons or keyboard
2. Click operation buttons or use keyboard shortcuts
3. Press `=` or `Enter` to calculate
4. Use `C` or `Escape` to clear
5. Use `⌫` or `Backspace` to delete last character

## Design Highlights

- **Gradient Background**: Purple to blue gradient for modern look
- **Glassmorphism**: Semi-transparent calculator with backdrop blur
- **Button Effects**: Hover and active states with shadows
- **Color Coding**: Different colors for numbers, operators, and equals
- **Responsive Grid**: Adapts to different screen sizes

## Error Handling

The backend gracefully handles:
- Division by zero (returns 400 error)
- Invalid operations (returns 400 error)
- Missing or invalid input (returns 422 error)
- General exceptions (returns 500 error)