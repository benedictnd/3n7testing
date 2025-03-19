import { cn } from "../../lib/utils";

interface SkeletonProps {
  className?: string;
  variant?: 'default' | 'circular' | 'rectangular' | 'text' | 'avatar' | 'card';
  width?: string | number;
  height?: string | number;
}

export function Skeleton({
  className,
  variant = 'default',
  width,
  height,
  ...props
}: SkeletonProps) {
  const baseClasses = "animate-pulse-slow bg-gray-200 dark:bg-gray-700 rounded";
  
  let variantClasses = '';
  switch (variant) {
    case 'circular':
      variantClasses = 'rounded-full';
      break;
    case 'text':
      variantClasses = 'h-4 w-2/3';
      break;
    case 'avatar':
      variantClasses = 'rounded-full h-10 w-10';
      break;
    case 'card':
      variantClasses = 'rounded-lg h-40 w-full';
      break;
    default:
      variantClasses = '';
  }

  return (
    <div
      className={cn(baseClasses, variantClasses, className)}
      style={{ 
        width: width ? (typeof width === 'number' ? `${width}px` : width) : undefined,
        height: height ? (typeof height === 'number' ? `${height}px` : height) : undefined 
      }}
      {...props}
    />
  );
}

interface SkeletonTextProps {
  className?: string;
  lines?: number;
  width?: string | number | Array<string | number>;
}

export function SkeletonText({ 
  className, 
  lines = 3, 
  width = ['100%', '80%', '60%'] 
}: SkeletonTextProps) {
  // Normalize width to array
  const widthArray = Array.isArray(width) ? width : Array(lines).fill(width);
  
  return (
    <div className={cn("space-y-2", className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton 
          key={i} 
          variant="text" 
          className="h-4" 
          width={widthArray[i % widthArray.length] || '100%'} 
        />
      ))}
    </div>
  );
}

export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn("space-y-3", className)}>
      <Skeleton variant="rectangular" className="h-40 w-full rounded-xl" />
      <SkeletonText lines={2} />
      <div className="flex justify-between">
        <Skeleton variant="text" width={80} />
        <Skeleton variant="text" width={40} />
      </div>
    </div>
  );
}

export function SkeletonAvatar({ className }: { className?: string }) {
  return (
    <div className={cn("flex items-center space-x-4", className)}>
      <Skeleton variant="avatar" />
      <div className="space-y-2">
        <Skeleton variant="text" width={120} />
        <Skeleton variant="text" width={80} />
      </div>
    </div>
  );
} 