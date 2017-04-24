function hello(times)
	double precision:: hello
	integer, intent(in):: times
	
	integer :: i = 1
	
	do i = 1, times
		write(*,*) "Hello World!"
	end do
	
	hello = 2.0d0 * times
end function hello
