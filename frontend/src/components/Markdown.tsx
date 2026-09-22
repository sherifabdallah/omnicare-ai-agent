import ReactMarkdown from 'react-markdown'

/** Renders assistant text (the model may answer in light markdown). Links open in a new tab. */
export function Markdown({ text }: { text: string }) {
  return (
    <div className="prose-entry">
      <ReactMarkdown
        components={{
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noreferrer">
              {children}
            </a>
          ),
        }}
      >
        {text}
      </ReactMarkdown>
    </div>
  )
}
