# PartSelect Chat Widget - Production Code

## Overview
HIII This is a production-ready React chat widget built with **JavaScript** (not TypeScript) and **plain CSS** (no Tailwind). It's designed for the PartSelect website with official brand colors.

## Brand Colors Used
- **Teal Green** (#0A6A63) - Primary, navigation, chat buttons
- **Golden Yellow** (#EFBF3F) - Support ribbon, accents
- **Orange/Tan** (#D98B2B) - House icon accent
- **Dark Gray** (#333333) - Text
- **Soft Gray** (#F5F5F5) - Background
- **White** (#FFFFFF) - Surfaces

## File Structure

```
src/
├── components/
│   └── chat/
│       ├── ChatWidget.jsx       # Main container with float button
│       ├── ChatWindow.jsx       # Chat window with messages
│       ├── MessageBubble.jsx    # Individual message component
│       ├── QuickActions.jsx     # Quick action chips
│       └── ChatWidget.css       # All chat widget styles
└── pages/
    ├── PartSelectDemo.jsx       # Demo page with PartSelect layout
    └── PartSelectDemo.css       # Demo page styles
```

## Features

### ✅ Implemented
- **Floating chat button** (bottom-right, teal green, hover effects)
- **Two display modes:**
  - Floating widget (380px width, 70vh height)
  - Expanded fullscreen mode
- **Smooth animations:**
  - Slide-up on open
  - Fade-in for messages
  - Typing indicator with animated dots
- **Quick action chips** (5 pre-defined options)
- **Auto-scroll** to latest message
- **Mock responses** (no backend needed)
- **Responsive design** (mobile & desktop)

### 🎨 Design Details
- Clean PartSelect header with logo + Selecto avatar
- Message bubbles with rounded corners
- Assistant (left, white) vs User (right, teal green)
- Typing indicator with bouncing dots
- Send button with paper plane icon

## How to Use in Your Project

### Option 1: Use in Current Lovable Project
The widget is already integrated! Just scroll to the top of the page to see the new production-style demo.

### Option 2: Extract for Standalone Use

1. **Copy these files to your React project:**
   ```
   src/components/chat/
   src/pages/PartSelectDemo.jsx
   src/pages/PartSelectDemo.css
   ```

2. **Import in your main component:**
   ```jsx
   import ChatWidget from './components/chat/ChatWidget';
   
   function App() {
     return (
       <div>
         <YourPageContent />
         <ChatWidget />
       </div>
     );
   }
   ```

3. **That's it!** The widget is self-contained with no external dependencies beyond React.

## Customization

### Change Colors
Edit `ChatWidget.css` at the top:
```css
:root {
  --teal-green: #0A6A63;    /* Your primary color */
  --golden-yellow: #EFBF3F; /* Your accent color */
  /* ... */
}
```

### Add More Quick Actions
Edit `ChatWindow.jsx`:
```jsx
const QUICK_ACTIONS = [
  { 
    id: 'custom', 
    label: 'Your Action', 
    response: 'Custom response text' 
  },
  // ... add more
];
```

### Change Widget Position
Edit `ChatWidget.css`:
```css
.chat-widget-container {
  bottom: 24px;  /* Adjust position */
  right: 24px;   /* Adjust position */
}
```

## Browser Support
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Technical Notes
- **No TypeScript** - Pure JavaScript (.jsx files)
- **No Tailwind** - Plain CSS with CSS variables
- **No backend** - All responses are mocked on frontend
- **React Hooks** - Uses `useState`, `useEffect`, `useRef`
- **Animations** - Pure CSS animations, no libraries

## Future Enhancements (Not Included)
- Real API integration
- User authentication
- Message persistence
- File uploads
- Voice input
- Multi-language support

## License
Proprietary - PartSelect internal use only
