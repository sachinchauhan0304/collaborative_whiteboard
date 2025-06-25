'use server';

import { db } from '@/lib/firebase';
import { DrawingAction } from '@/lib/types';
import { doc, getDoc, setDoc, addDoc, collection, serverTimestamp } from 'firebase/firestore';

export async function saveCanvas(boardId: string, canvasState: string) {
  try {
    const timestamp = new Date();
    await setDoc(doc(db, 'boards', boardId), {
      canvasState,
      updatedAt: timestamp,
    });
    return { success: true, updatedAt: timestamp };
  } catch (error: any) {
    console.error('Error saving canvas:', error);
    return { success: false, error: error.message };
  }
}

export async function loadCanvas(boardId: string) {
  try {
    const docRef = doc(db, 'boards', boardId);
    const docSnap = await getDoc(docRef);

    if (docSnap.exists()) {
      const data = docSnap.data();
      return { success: true, data: { canvasState: data.canvasState, updatedAt: data.updatedAt.toDate() } };
    } else {
      return { success: true, data: null };
    }
  } catch (error: any) {
    console.error('Error loading canvas:', error);
    return { success: false, error: error.message };
  }
}

export async function addDrawingAction(boardId: string, action: DrawingAction) {
  try {
    const actionsRef = collection(db, 'boards', boardId, 'actions');
    await addDoc(actionsRef, { ...action, timestamp: serverTimestamp() });
    return { success: true };
  } catch (error: any) {
    console.error('Error adding drawing action:', error);
    return { success: false, error: error.message };
  }
}
