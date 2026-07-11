import React from "react";

interface Activity {
  id: string;
  type: string;
  description: string;
  timestamp: string;
  icon: string;
}

export default function CustomerTimeline({ activities = [] }: { activities?: any[] }) {
  return (
    <div className="flow-root p-6">
      {activities.length === 0 && (
        <div className="text-center py-10 text-gray-400 italic text-sm">
          No activity recorded yet.
        </div>
      )}
      <ul role="list" className="-mb-8">
        {activities.map((activity, idx) => (
          <li key={activity.id}>
            <div className="relative pb-8">
              {idx !== activities.length - 1 ? (
                <span className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true" />
              ) : null}
              <div className="relative flex space-x-3">
                <div>
                  <span className="h-8 w-8 rounded-full bg-gray-50 flex items-center justify-center ring-8 ring-white text-sm">
                    {activity.activity_type === "booking" ? "📅" : activity.activity_type === "chat" ? "💬" : "📝"}
                  </span>
                </div>
                <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                  <div>
                    <p className="text-sm text-gray-500">
                      {activity.description}
                    </p>
                  </div>
                  <div className="whitespace-nowrap text-right text-xs text-gray-400">
                    <time dateTime={activity.created_at}>{new Date(activity.created_at).toLocaleString()}</time>
                  </div>
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
