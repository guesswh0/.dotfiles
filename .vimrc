" basic settings
set encoding=UTF-8

set mouse=a
set cursorline

set number
set relativenumber

" indent
set smarttab
set autoindent
set shiftwidth=4
set tabstop=4
set softtabstop=4

" Ctrl+Shift+up move line above"
nmap <C-S-Up> m -2<CR>

" Ctrl+Shift+down move line below
nmap <C-S-Down> m +1<CR>

" builtin plugins
syntax enable
filetype plugin indent on

" vim-plug plugins
call plug#begin()
" :PlugInstall, :PlugUpdate, :PlugClean

Plug 'nordtheme/vim' " Nord theme
Plug 'preservim/nerdtree' " NerdTree
Plug 'vim-airline/vim-airline' " Status bar

call plug#end()

" color theme
set termguicolors
:colorscheme nord

" NERDTree
set <A-1>=1 " Alt+1
nnoremap <A-1> :NERDTreeToggle<CR>

" autocmds
augroup languages
    autocmd!
    autocmd FileType python xnoremap <leader>r <esc>:'<,'>:w !python3<CR>
    autocmd FileType go set noexpandtab
    autocmd FileType html,javascript,css,json,yaml,sh
                \ setlocal ts=2 sts=2 sw=2 expandtab
augroup END

" terminal
set splitbelow
set termwinsize=10x0

" open / close terminal with F12
nnoremap <F12> :term<CR>
tnoremap <F12> <C-\><C-n>:bdelete!<CR>
