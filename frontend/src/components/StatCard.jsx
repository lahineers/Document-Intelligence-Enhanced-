export default function StatCard(props) {
  return (
    <div className="bg-white rounded-lg shadow p-5">
      <p className="text-gray-500">
        {props.title}
      </p>

      <h2 className="text-3xl font-bold mt-2">
        {props.value}
      </h2>
    </div>
  );
}