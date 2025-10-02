" basic settings
set encoding=UTF-8
set termguicolors

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

" terminal
set splitbelow
set termwinsize=15x0

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
:colorscheme nord

" autocmds
augroup languages
    autocmd!
    " execute selected python code
    autocmd FileType python xnoremap <leader>r <esc>:'<,'>:w !python3<CR>
    autocmd FileType go set noexpandtab
    autocmd FileType html,javascript,css,json,yaml,sh
                \ setlocal ts=2 sts=2 sw=2 expandtab
augroup END

" NERDTree
set <A-1>=1 " Alt+1
nnoremap <A-1> :NERDTreeToggle<CR>
let NERDTreeShowHidden=1

" move lines up and down"
nmap <C-S-Up> m -2<CR>
nmap <C-S-Down> m +1<CR>

" open / close terminal with F12
nnoremap <F12> :term<CR>
tnoremap <F12> <C-\><C-n>:bdelete!<CR>

" exit terminal with <Esc>
tnoremap <Esc> <C-\><C-n>

" F5 copy to clipboard
nnoremap <F5> :%y+<CR>
