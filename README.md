# CollabDraw
![alt text](<Screenshot 2025-06-24 003702.png>)
CollabDraw is a real-time collaborative whiteboard application designed for seamless brainstorming, planning, and creative sessions. Built with a modern tech stack, it provides an intuitive and responsive experience for users to draw, write, and innovate together from anywhere.



## ✨ Features

- **Real-time Collaboration**: See what your teammates are drawing instantly.
- **Rich Drawing Tools**: Pen, line, rectangle, circle, and text tools.
- **Customization**: Change brush size and color with an easy-to-use picker.
- **Undo/Redo**: Easily correct mistakes.
- **Save & Load**: Your work is automatically saved to the cloud. You can also manually save and load different board states.
- **Export**: Download your masterpiece as a PNG image.
- **AI Backgrounds**: Use AI to generate a creative background for your canvas.
- **Responsive Design**: Works on all devices, from desktops to tablets.

## 🛠️ Tech Stack

- **Framework**: [Next.js](https://nextjs.org/) (App Router)
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **UI Components**: [ShadCN UI](https://ui.shadcn.com/)
- **Real-time Database**: [Firebase Firestore](https://firebase.google.com/docs/firestore)
- **Icons**: [Lucide React](https://lucide.dev/)
- **AI Features**: [Genkit](https://firebase.google.com/docs/genkit)

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- [Node.js](https://nodejs.org/en/) (v18 or later recommended)
- `npm` or your preferred package manager

### Installation

1.  **Clone the repository** (or download the source code):
    ```bash
    git clone [https://github.com/sachinchauhan0304/collaborative_whiteboard.git]
    cd collab-draw
    ```

2.  **Install dependencies**:
    ```bash
    npm install
    ```

3.  **Set up Firebase**:
    - Go to the [Firebase Console](https://console.firebase.google.com/) and create a new project.
    - In your project dashboard, go to **Project Settings** > **General**.
    - Under "Your apps", create a new Web App (`</>`).
    - Copy the `firebaseConfig` object. It will look something like this:
      ```javascript
      const firebaseConfig = {
        apiKey: "AIza...",
        authDomain: "your-project-id.firebaseapp.com",
        projectId: "your-project-id",
        storageBucket: "your-project-id.appspot.com",
        messagingSenderId: "1234567890",
        appId: "1:12345:web:abcdef123"
      };
      ```
    - Go to the **Build** > **Firestore Database** section in the Firebase console and create a database. Start in **test mode** for easy development (you can set up security rules later).

4.  **Set up environment variables**:
    - Create a file named `.env.local` in the root of your project.
    - Add your Firebase configuration keys to this file:
      ```
      NEXT_PUBLIC_FIREBASE_API_KEY=AIza...
      NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
      NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
      NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
      NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=1234567890
      NEXT_PUBLIC_FIREBASE_APP_ID=1:12345:web:abcdef123
      ```

### Running the Application

1.  **Start the development server**:
    ```bash
    npm run dev
    ```
    Open [http://localhost:9002](http://localhost:9002) with your browser to see the result.

2.  **To create a new board**:
    - Simply click the "Create a new board" button on the homepage.
    - Share the URL with others to start collaborating!

## 📜 Available Scripts

In the project directory, you can run:

- `npm run dev`: Runs the app in development mode.
- `npm run build`: Builds the app for production.
- `npm run start`: Starts a Next.js production server.
- `npm run lint`: Lints the project files.

## working link
(https://collaborativewhiteboard-cgmzxr4pugq2w7hhsgifbh.streamlit.app/)
