/** Inline 20px icon set (stroke-based) so the app needs no icon dependency. */
import type { SVGProps } from 'react'

type Props = SVGProps<SVGSVGElement>

function Icon({ children, ...props }: Props) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...props}
    >
      {children}
    </svg>
  )
}

export const ShieldIcon = (p: Props) => (
  <Icon {...p}>
    <path d="M12 3l7 2.8v5.4c0 4.4-2.9 8.4-7 9.8-4.1-1.4-7-5.4-7-9.8V5.8L12 3z" />
  </Icon>
)

export const SendIcon = (p: Props) => (
  <Icon {...p}>
    <path d="M4.5 12h14M13 6.5l5.5 5.5L13 17.5" />
  </Icon>
)

export const PlusIcon = (p: Props) => (
  <Icon {...p}>
    <path d="M12 5v14M5 12h14" />
  </Icon>
)

export const BookIcon = (p: Props) => (
  <Icon {...p}>
    <path d="M4 5.5A1.5 1.5 0 015.5 4H10a2 2 0 012 2v13a1.5 1.5 0 00-1.5-1.5H5.5A1.5 1.5 0 014 16V5.5z" />
    <path d="M20 5.5A1.5 1.5 0 0018.5 4H14a2 2 0 00-2 2v13a1.5 1.5 0 011.5-1.5h5A1.5 1.5 0 0020 16V5.5z" />
  </Icon>
)

export const SearchIcon = (p: Props) => (
  <Icon {...p}>
    <circle cx="11" cy="11" r="6.5" />
    <path d="M16 16l4 4" />
  </Icon>
)

export const FileIcon = (p: Props) => (
  <Icon {...p}>
    <path d="M14 3H7a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8l-5-5z" />
    <path d="M14 3v5h5M9 13h6M9 17h4" />
  </Icon>
)

export const PlusFileIcon = (p: Props) => (
  <Icon {...p}>
    <path d="M14 3H7a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8l-5-5z" />
    <path d="M14 3v5h5M12 11v6M9 14h6" />
  </Icon>
)

export const CheckIcon = (p: Props) => (
  <Icon {...p}>
    <path d="M5 12.5l4.5 4.5L19 7.5" />
  </Icon>
)

export const AlertIcon = (p: Props) => (
  <Icon {...p}>
    <path d="M12 8v5M12 16.5v.5" />
    <path d="M10.3 4.3L3 17a2 2 0 001.7 3h14.6a2 2 0 001.7-3L13.7 4.3a2 2 0 00-3.4 0z" />
  </Icon>
)

export const ChevronIcon = (p: Props) => (
  <Icon {...p}>
    <path d="M8.5 5l7 7-7 7" />
  </Icon>
)

export const SunIcon = (p: Props) => (
  <Icon {...p}>
    <circle cx="12" cy="12" r="4" />
    <path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.2 5.2l1.4 1.4M17.4 17.4l1.4 1.4M18.8 5.2l-1.4 1.4M6.6 17.4l-1.4 1.4" />
  </Icon>
)

export const MoonIcon = (p: Props) => (
  <Icon {...p}>
    <path d="M20 14.5A8 8 0 019.5 4a8 8 0 1010.5 10.5z" />
  </Icon>
)

export const MenuIcon = (p: Props) => (
  <Icon {...p}>
    <path d="M4 7h16M4 12h16M4 17h16" />
  </Icon>
)

export const CloseIcon = (p: Props) => (
  <Icon {...p}>
    <path d="M6 6l12 12M18 6L6 18" />
  </Icon>
)

export const UserIcon = (p: Props) => (
  <Icon {...p}>
    <circle cx="12" cy="8" r="3.5" />
    <path d="M4.5 20a7.5 7.5 0 0115 0" />
  </Icon>
)

export const ToolIcon = (p: Props) => (
  <Icon {...p}>
    <path d="M14.5 6.5a4 4 0 005.2 5.2l-7.4 7.4a2.5 2.5 0 01-3.5-3.5l7.4-7.4a4 4 0 00-1.7-1.7z" />
    <path d="M9.5 4.5L4 10l2.5 2.5" />
  </Icon>
)
