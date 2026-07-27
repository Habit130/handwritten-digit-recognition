import type { CodeFile } from "../lib/types";

interface CodePaneProps {
  files: CodeFile[];
  selectedPath: string | null;
  onSelectPath: (path: string) => void;
  activeAnchor?: string;
}

export function CodePane({
  files,
  selectedPath,
  onSelectPath,
  activeAnchor,
}: CodePaneProps) {
  const selected =
    files.find((file) => file.path === selectedPath) ?? files[0];

  return (
    <div className="code-pane">
      <div className="code-tabs">
        {files.map((file) => (
          <button
            type="button"
            className={selected?.path === file.path ? "is-active" : ""}
            key={file.path}
            onClick={() => onSelectPath(file.path)}
          >
            {file.path.split("/").at(-1)}
          </button>
        ))}
      </div>
      {selected !== undefined ? (
        <>
          <div className="code-path">{selected.path}</div>
          <pre>
            <code>
              {selected.content.split("\n").map((line, index) => (
                <span
                  className={
                    activeAnchor !== undefined &&
                    line.includes(`# ${activeAnchor}`)
                      ? "is-highlighted"
                      : ""
                  }
                  key={`${index}-${line}`}
                >
                  <i>{String(index + 1).padStart(3, "0")}</i>
                  {line || " "}
                </span>
              ))}
            </code>
          </pre>
        </>
      ) : (
        <div className="code-empty">正在读取本地源文件…</div>
      )}
    </div>
  );
}
