export default function Sidebar() {
  return (
    <div className="w-64 h-screen border-r bg-white p-6">
      <h1 className="text-2xl font-bold">
        DocIntelli
      </h1>

      <div className="mt-10 space-y-4">
        <p className="cursor-pointer">
          Dashboard
        </p>

        <p className="cursor-pointer">
          Documents
        </p>

        <p className="cursor-pointer">
          Query
        </p>

        <p className="cursor-pointer">
          Compare
        </p>
      </div>
    </div>
  );
}