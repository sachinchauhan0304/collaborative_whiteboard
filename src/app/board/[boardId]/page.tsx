import CollabDraw from '@/components/collab-draw';

export default function BoardPage({ params }: { params: { boardId: string } }) {
  return <CollabDraw boardId={params.boardId} />;
}
