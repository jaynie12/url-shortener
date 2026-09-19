import { FormEvent, useState } from 'react'
import './App.css'

function App() {
  const [longUrl, setLongUrl] = useState('')
  const [shortUrl, setShortUrl] = useState('')
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  function shortenUrl(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setCopied(false)

    try {
      const url = new URL(longUrl)
      if (!['http:', 'https:'].includes(url.protocol)) throw new Error('Unsupported protocol')

      const slug = crypto.randomUUID().slice(0, 6)
      setShortUrl(`${window.location.origin}/${slug}`)
      setError('')
    } catch {
      setShortUrl('')
      setError('Enter a valid URL beginning with http:// or https://')
    }
  }

  async function copyShortUrl() {
    await navigator.clipboard.writeText(shortUrl)
    setCopied(true)
  }

  return (
    <main className="page-shell">
      <div className="brand-mark" aria-hidden="true">//</div>
      <p className="eyebrow">A tiny link utility</p>
      <h1>Make links<br /><em>lighter.</em></h1>
      <p className="intro">Paste a long URL below and get a compact link to share anywhere.</p>

      <form className="shortener-form" onSubmit={shortenUrl}>
        <label htmlFor="long-url">Your long URL</label>
        <div className="input-row">
          <input
            id="long-url"
            type="url"
            value={longUrl}
            onChange={(event) => setLongUrl(event.target.value)}
            placeholder="https://example.com/my-very-long-link"
            aria-describedby={error ? 'url-error' : undefined}
            required
          />
          <button type="submit">Shorten <span aria-hidden="true">↗</span></button>
        </div>
        {error && <p className="error" id="url-error">{error}</p>}
      </form>

      {shortUrl && (
        <section className="result" aria-live="polite">
          <div>
            <p className="result-label">Your short link</p>
            <a href={shortUrl}>{shortUrl}</a>
          </div>
          <button className="copy-button" type="button" onClick={copyShortUrl}>
            {copied ? 'Copied' : 'Copy'}
          </button>
        </section>
      )}

      <footer>Fast, simple, and made for sharing.</footer>
    </main>
  )
}

export default App
