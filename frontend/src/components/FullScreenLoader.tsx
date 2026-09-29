import { Skeleton } from "./Skeleton";

export function FullScreenLoader() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <Skeleton className="h-16 w-72" />
    </div>
  );
}
