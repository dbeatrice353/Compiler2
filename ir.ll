@y = global i8* zeroinitializer
@z = global [100 x i8] zeroinitializer
@x = global i32 zeroinitializer
define void @p1(){
ret void
}
define void @p2(){
ret void
}
define void @p3(){
ret void
}
define void @p4(){
ret void
}
define void @p5(){
ret void
}
define void @p6(){
ret void
}
define i32 @main(){
%y = alloca i8*
%z = alloca [100 x i8]
%x = alloca i32
%f = alloca double
%fa = alloca [10 x double]
%i = alloca i32
%ia = alloca [5 x i32]
%c = alloca i8
%ca = alloca [20 x i8]
%b = alloca i1
%ba = alloca [15 x i1]
%s = alloca i8*
%r0 = fdiv double 2.45e+00, 5.0e+00
%r1 = fadd double 3.14e+00, %r0
%r2 = fsub double 4.56e+00, 3.0e+00
%r3 = sub nsw i32 9, 1
%r4 = add nsw i32 %r3, 5
%r5 = add nsw i32 2, %r4
%r6 = add nsw i32 6, 5
%r7 = or i1 0, 1
%r8 = and i1 1, 0
ret i32 0
}
