.section .text,"ax",@progbits
.globl entry_code
entry_code:
 mflr 0
 stdu 1,-128(1)
 std 0,112(1)
 lis 12,native_main@ha
 addi 12,12,native_main@l
 ld 2,8(12)
 ld 12,0(12)
 mtctr 12
 bctrl
 li 11,3
 sc
 b .
.section .rodata,"a",@progbits
.balign 8
.globl _start
_start:
 .long entry_code
 .long entry_code
 .quad 0,0
.section .sys_proc_param,"a",@progbits
.balign 8
 .long 32,0x13bcc5f6,0x00009000,0x00192001,1000,0x10000,0x100000,0

	.align 2
	.section ".lib.ent","a"
	
	.align 2
	.section ".lib.stub","a"
	
	.align 2
	.section ".sys_proc_prx_param","a"
	.long 0x28
	.long 0x1b434cec
	.long 2
	.long 0
	.long __libentstart
	.long __libentend
	.long __libstubstart
	.long __libstubend
	.short 0x0101
	.short 0
	.long 0
	
.section .sceversion,"a",@progbits
.asciz "01.9200"
