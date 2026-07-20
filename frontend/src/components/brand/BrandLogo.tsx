import { useState } from 'react'

interface BrandLogoProps {
  name: string
  website?: string | null
  logoUrl?: string | null
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
}

const sizeMap = {
  sm: 'w-8 h-8 text-base',
  md: 'w-12 h-12 text-lg',
  lg: 'w-20 h-20 text-3xl lg:w-24 lg:h-24 text-4xl',
  xl: 'w-24 h-24 text-4xl',
}

function extractDomain(url: string): string | null {
  try {
    if (!url.startsWith('http')) url = 'https://' + url
    const u = new URL(url)
    return u.hostname.replace(/^www\./, '')
  } catch {
    return null
  }
}

export default function BrandLogo({ name, website, logoUrl, size = 'md', className = '' }: BrandLogoProps) {
  const [sourceIndex, setSourceIndex] = useState(0)
  const [error, setError] = useState(false)

  const initial = name.charAt(0).toUpperCase()
  const colorClasses = 'bg-primary-100 dark:bg-primary-900/40 text-primary-600 dark:text-primary-400'
  const sizeClasses = sizeMap[size]

  if (!logoUrl || error) {
    return (
      <div className={`${sizeClasses} rounded-2xl ${colorClasses} flex items-center justify-center flex-shrink-0 ${className}`}>
        <span className="font-bold">{initial}</span>
      </div>
    )
  }

  const domain = website ? extractDomain(website) : null

  // Multiple favicon sources for robustness
  const sources = [logoUrl]
  if (domain) {
    sources.push(`https://icon.horse/icon/${domain}`)
    sources.push(`https://www.google.com/s2/favicons?domain=${domain}&sz=128`)
    sources.push(`https://icons.duckduckgo.com/ip3/${domain}.ico`)
  }

  const currentSrc = sources[sourceIndex] || null

  if (!currentSrc) {
    return (
      <div className={`${sizeClasses} rounded-2xl ${colorClasses} flex items-center justify-center flex-shrink-0 ${className}`}>
        <span className="font-bold">{initial}</span>
      </div>
    )
  }

  const handleError = () => {
    if (sourceIndex < sources.length - 1) {
      setSourceIndex(sourceIndex + 1)
    } else {
      setError(true)
    }
  }

  return (
    <img
      src={currentSrc}
      alt={name}
      onError={handleError}
      className={`${sizeClasses} rounded-2xl object-cover flex-shrink-0 ${className}`}
      loading="lazy"
    />
  )
}
