type TabType = {
    label: string
}
const tab: TabType[] = [
    { label: "espoir" },
    { label: "force" },
    { label: "Loemba" },
    { label: "Loea" },
    { label: "klkl" },
    { label: "hope" },
]

export function Card() {
    return (
        <div className="flex-1 flex gap-2 caret-indigo-300 border p-2 px-4 rounded-lg">
            {tab.map((e) => (
                <p key={e.label}>{e.label}</p>
            ))}
        </div>
    )
}