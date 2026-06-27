# Design System

O design system está em `design_system/design-system.html` e é baseado no sistema visual da FIESC. Abra o arquivo no navegador para visualizar todos os componentes.

## Fonte

**MuseoSans** em três pesos:

| Peso | Uso |
|---|---|
| 300 | Corpo de texto leve |
| 500 | Texto padrão / labels |
| 700 | Títulos / destaque |

## Tokens de cor

| Token CSS | Valor | Uso |
|---|---|---|
| `--fsi-clr-1` / `--fsi-clr-primaria` | `hsl(220 74% 33%)` | Cor primária (azul) |
| `--fsi-clr-2` | `hsl(212 100% 90%)` | Azul claro |
| `--fsi-clr-3` | `hsl(212 100% 90% / 0.32)` | Azul claro transparente |
| `--fsi-clr-4` | `hsl(0 0% 16%)` | Texto escuro |
| `--fsi-clr-5` | `hsl(0 0% 96%)` | Background padrão |
| `--fsi-clr-6` | `hsl(0 0% 100%)` | Branco |
| `--fsi-clr-7` | `hsl(0 0% 7%)` | Preto |
| `--fsi-clr-8` | `hsl(232 86% 22%)` | Azul escuro |
| `--fsi-clr-txt` | `#333333` | Cor padrão de texto |
| `--fsi-clr-button` | `hsl(239 79% 29%)` | Background de botões |
| `--fsi-clr-button-hover` | `#005ca9` | Hover de botões |

## Escala tipográfica

| Token | Valor |
|---|---|
| `--fs-100` | `0.8rem` |
| `--fs-200` | `0.9rem` |
| `--fs-300` | `1rem` |
| `--fs-400` | `1.25rem` |
| `--fs-500` | `1.5rem` |
| `--fs-600` | `1.75rem` |
| `--fs-700` | `2rem` |
| `--fs-800` | `2.5rem` |

## Outros tokens

| Token | Valor | Uso |
|---|---|---|
| `--fsi-border-rad` | `20px` | Border radius padrão |
| `--fsi-pad-bl` | `2.5rem` | Padding de blocos |
| `--fsi-shadow-1` | `rgb(99 99 99 / 0.2) 0px 2px 8px 0px` | Sombra padrão |

## Componentes disponíveis no HTML

O arquivo `design-system.html` inclui os seguintes componentes prontos para referência:

- Botões (`fsi-cta`) — primário, negativo, wired, link
- Tipografia e headings
- Cards e blocos de conteúdo
- Mega-menu de navegação
- Ícones (FontAwesome 4.7 + Material Icons)

## Acessibilidade

- HTML semântico: `header`, `nav`, `main`, `section`, `article`, `aside`, `footer`
- **VLibras** integrado em todas as páginas
- Contraste e navegação por teclado seguindo boas práticas WCAG
- Foco visível: `outline: 3px solid rgba(0,125,250,0.7)` em elementos interativos
