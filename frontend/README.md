# PartSelect Chat Agent - Frontend

Modern React-based chat interface for the PartSelect chat agent, featuring PartSelect branding, rich metadata display, and responsive design.

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Setup](#setup)
- [Architecture](#architecture)
- [Components](#components)
- [Styling](#styling)
- [API Integration](#api-integration)
- [Building & Deployment](#building--deployment)

## 🎯 Overview

The frontend is built with **React** and provides:
- **Branded UI** using PartSelect colors and design system
- **Rich Chat Interface** with product cards, order cards, and interactive buttons
- **Quick Actions** with starter text and example prompts
- **Responsive Design** for desktop and mobile
- **Smooth Animations** and transitions

## 🛠️ Tech Stack

- **React 18** - UI framework
- **TypeScript/JavaScript** - Type safety
- **Vite** - Build tool
- **CSS** - Custom styling (no Tailwind in chat widget)
- **shadcn/ui** - UI components (for demo pages)

## 🚀 Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Configuration

Create `.env.local` (optional):

```bash
VITE_API_BASE_URL=http://localhost:8000
```

### Development

```bash
npm run dev
```

Frontend runs at: `http://localhost:5173`

**Note**: Make sure the backend is running at `http://localhost:8000`

## 🏗️ Architecture

### Directory Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── chat/              # Chat widget components
│   │   │   ├── ChatWidget.jsx      # Main container
│   │   │   ├── ChatWindow.jsx      # Chat window
│   │   │   ├── MessageBubble.jsx   # Message component
│   │   │   ├── ProductCard.jsx     # Product display
│   │   │   ├── OrderCard.jsx       # Order display
│   │   │   ├── LinkButtons.jsx     # Action buttons
│   │   │   ├── QuickActions.jsx    # Quick action chips
│   │   │   └── ChatWidget.css      # All styles
│   │   │
│   │   ├── ChatBot.tsx        # Alternative chat component
│   │   └── ui/                # shadcn/ui components
│   │
│   ├── api/
│   │   └── chat.ts            # API client
│   │
│   ├── pages/
│   │   ├── Index.tsx          # Main page
│   │   ├── PartSelectDemo.jsx # Demo page
│   │   └── NotFound.tsx       # 404 page
│   │
│   └── assets/
│       └── ps-logo.svg        # PartSelect logo
│
├── public/
└── package.json
```

### Component Hierarchy

```
ChatWidget (Container)
  └── ChatWindow
      ├── Header (Logo + Controls)
      ├── Messages Area
      │   └── MessageBubble[]
      │       ├── ProductCard (if metadata.type === 'product_info')
      │       ├── OrderCard (if metadata.type === 'order_info')
      │       └── LinkButtons (if metadata.type === 'links')
      ├── Quick Actions (if no messages)
      └── Input Area
          ├── Text Input
          └── Send Button
```

## 🧩 Components

### ChatWidget

Main container component with floating button.

**Props:**
- None (self-contained)

**Features:**
- Floating button (bottom-right)
- Expandable window
- Two modes: floating (380px) and expanded (fullscreen)

### ChatWindow

Main chat window component.

**Props:**
- `isExpanded`: boolean
- `setIsExpanded`: function
- `onClose`: function

**State:**
- `messages`: Array of message objects
- `inputValue`: Current input text
- `isLoading`: Loading state
- `currentExamples`: Currently displayed example prompts

### MessageBubble

Individual message component.

**Props:**
- `message`: Message object
- `onPrompt`: Function to send prompt

**Message Object:**
```typescript
{
  id: number;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  metadata?: {
    type: 'product_info' | 'order_info' | 'links';
    product?: ProductData;
    order?: OrderData;
    links?: LinkData[];
  };
}
```

### ProductCard

Displays product information.

**Props:**
- `product`: Product data object
- `onPrompt`: Function to send prompt

**Product Data:**
```typescript
{
  id: string;              // Part ID (e.g., PS11752778)
  name: string;            // Part name
  price: number;           // Price
  url: string;             // Product URL
  brand?: string;          // Brand name
  applianceType?: string;   // "refrigerator" or "dishwasher"
  installDifficulty?: string;
  installTime?: string;
}
```

**Features:**
- Price display
- Install difficulty badge
- "View product" button
- "Check compatibility" button

### OrderCard

Displays order information.

**Props:**
- `order`: Order data object
- `onPrompt`: Function to send prompt

**Order Data:**
```typescript
{
  id: string;              // Order ID
  status: string;          // Order status
  date: string;            // Order date
  amount: number;          // Order amount
  shippingType?: string;
  partName?: string;
  partId?: string;
  partUrl?: string;
  transactionStatus?: string;
  returnEligible: boolean;
}
```

**Features:**
- Status badge with color coding
- Order details
- "View part" button
- "Return order" button (if eligible)
- "Chat about Return" button

### LinkButtons

Displays action buttons (repair guides, blog, etc.).

**Props:**
- `links`: Array of link objects
- `onAction`: Function (optional)

**Link Data:**
```typescript
{
  label: string;  // Button text
  url: string;    // Link URL
}
```

### QuickActions

Quick action chips with starter text and examples.

**Features:**
- 4 quick actions:
  - Get repair help
  - Find compatible parts
  - Help me with my order
  - How do I use this?
- Each action shows:
  - Starter text (assistant message)
  - Example prompts (clickable chips)

## 🎨 Styling

### Brand Colors

```css
:root {
  --teal-green: #0A6A63;      /* Primary color */
  --golden-yellow: #EFBF3F;    /* Accent color */
  --orange-tan: #D98B2B;       /* Secondary accent */
  --dark-gray: #333333;        /* Text color */
  --soft-gray: #F5F5F5;        /* Background */
  --white: #FFFFFF;            /* Surfaces */
}
```

### Key Styles

- **Chat Widget**: Fixed position, bottom-right
- **Message Bubbles**: Rounded corners, color-coded (user: teal, assistant: white)
- **Cards**: Shadow, rounded corners, structured layout
- **Buttons**: Teal primary, gray secondary
- **Animations**: Slide-up, fade-in, typing indicator

### Responsive Design

- **Desktop**: 380px floating widget, expandable to fullscreen
- **Mobile**: Full-width, max-height constraints
- **Breakpoints**: Handled via CSS media queries

## 🔌 API Integration

### API Client

Located in `src/api/chat.ts`:

```typescript
export async function sendChatMessage(
  message: string
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  return response.json();
}
```

### Response Format

```typescript
interface ChatResponse {
  reply: string;
  metadata?: {
    type: 'product_info' | 'order_info' | 'links';
    product?: ProductData;
    order?: OrderData;
    links?: LinkData[];
  };
}
```

### Error Handling

- Network errors: Display error message
- API errors: Show user-friendly error
- Loading states: Typing indicator

## 🏗️ Building & Deployment

### Build

```bash
npm run build
```

Output: `dist/` directory

### Preview

```bash
npm run preview
```

### Deployment

Deploy `dist/` to any static hosting:

**Vercel:**
```bash
npm install -g vercel
vercel
```

**Netlify:**
- Drag and drop `dist/` folder
- Or use Netlify CLI

**Other:**
- Upload `dist/` to any static hosting service

### Environment Variables

Set `VITE_API_BASE_URL` to production backend URL:

```bash
VITE_API_BASE_URL=https://api.partselect.com
```

## 🧪 Testing

### Linting

```bash
npm run lint
```

### Build Check

```bash
npm run build
```

### Manual Testing

1. Test all quick actions
2. Test product card interactions
3. Test order card interactions
4. Test responsive design
5. Test error handling

## 🎯 Features

### Implemented

✅ Floating chat button
✅ Expandable chat window
✅ Message bubbles (user/assistant)
✅ Product cards with actions
✅ Order cards with actions
✅ Link buttons
✅ Quick actions with examples
✅ Typing indicator
✅ Auto-scroll
✅ Responsive design
✅ PartSelect branding
✅ Smooth animations

### Future Enhancements

- [ ] Conversation history persistence
- [ ] Multi-turn conversation context
- [ ] Voice input
- [ ] File uploads (for part photos)
- [ ] Dark mode
- [ ] Internationalization

## 📱 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 🔧 Troubleshooting

### "Cannot connect to backend"

- Check `VITE_API_BASE_URL` in `.env.local`
- Ensure backend is running
- Check CORS settings

### "Build fails"

- Clear `node_modules` and reinstall
- Check Node.js version (18+)
- Check for TypeScript errors

### "Styles not loading"

- Check `ChatWidget.css` import
- Verify CSS file paths
- Check for CSS conflicts

## 📚 Additional Resources

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [PartSelect Brand Guidelines](https://www.partselect.com/)
