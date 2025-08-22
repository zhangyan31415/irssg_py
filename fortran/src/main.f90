program irvsp 
    use get_ssg
    use comms 
    use init
    use wave_data
    use linear_rep
    use comprel
    implicit none 

    integer            :: kkk

    ! command argument 
    integer            :: narg, iarg, lens, stat 
    character(len=100) :: arg, cmd 

    integer,     allocatable :: rot(:,:,:)
    real(dp),     allocatable :: spin_rot(:,:,:)
    real(dp),    allocatable :: SO3(:,:,:)
    real(dp),    allocatable :: tau(:,:)
    complex(dp), allocatable :: SU2(:,:,:)
    complex(dp), allocatable :: kphase(:)
    complex(dp), allocatable :: Gphase(:,:)
    integer,     allocatable :: tilte_vec(:,:)
    integer,     allocatable :: litt_group(:)
    integer,     allocatable :: time_reversal(:)
    integer     ::           num_litt_group
    integer     ::          num_litt_group_unitary
    integer, allocatable :: litt_group_unitary(:)
    integer, allocatable :: rot_unitary(:,:,:)
    real(dp), allocatable :: SO3_unitary(:,:,:)
    complex(dp), allocatable :: SU2_unitary(:,:,:)
    real(dp), allocatable :: tau_unitary(:,:)
    integer :: irrep_num
    integer :: irrep_unitary_num
    integer, allocatable :: op_order(:)
    complex(dp), allocatable :: ch_table(:,:)
    complex(dp), allocatable :: ch_table_less(:,:)

    complex(dp), allocatable :: ch_unitary_table(:,:)
    complex(dp), allocatable :: ch_unitary_table_less(:,:)

    integer, allocatable :: irrep_coirrep_relation(:,:)

    character(len=15),allocatable :: irrep_name_list(:)

    integer:: kchoose_start, kchoose_end
    logical :: kchoose_flag
    logical :: spin_no_reversal
    integer, allocatable :: torsion(:)
    integer, allocatable :: discriminant_value(:)

    character(len=4) :: k_name
    character(len=15) :: k_frac_symbol

    integer :: i, j
    complex(dp), allocatable :: phase(:)
    character(len=15) :: ssg_num

    



interface
subroutine irrep_ssg(num_litt_group_unitary,litt_group_unitary, rot, tau,&
                      SO3, SU2, &
                      KKK, WK, kphase, &
                      num_bands, m, n, ene_bands, &
                      dim_basis, num_basis, &
                      coeffa, coeffb, irrep_num, ch_table, &
                      irrep_name_list, &
                      G_phase_pw, rot_vec_pw)

    integer, parameter :: dp = 8
    integer, intent(in) :: num_litt_group_unitary
    integer,     intent(in) :: rot(3,3,num_litt_group_unitary)
    real(dp),    intent(in) :: tau(3,num_litt_group_unitary)
    real(dp),    intent(in) :: SO3(3,3,num_litt_group_unitary)
    complex(dp), intent(in) :: SU2(2,2,num_litt_group_unitary)
    integer,     intent(in) :: litt_group_unitary(num_litt_group_unitary)
    integer,     intent(in) :: KKK 
    real(dp),    intent(in) :: WK(3)
    complex(dp), intent(in) :: kphase(num_litt_group_unitary)

    integer,     intent(in) :: num_bands, m, n 
    real(dp),    intent(in) :: ene_bands(num_bands) 

    integer,     intent(in) :: dim_basis, num_basis  
    complex(dp), intent(in) :: coeffa(dim_basis, num_bands)
    complex(dp), intent(in) :: coeffb(dim_basis, num_bands)

    integer, intent(in) :: irrep_num
    character(len=15), intent(in) :: irrep_name_list(irrep_num)
    complex(dp), intent(in) :: ch_table(irrep_num,num_litt_group_unitary)
    complex(dp), intent(in), optional :: G_phase_pw(dim_basis, num_litt_group_unitary)
    integer,     intent(in), optional :: rot_vec_pw(dim_basis, num_litt_group_unitary)


end subroutine irrep_ssg
end interface 
    call load_bilbao(100)
    
    kchoose_flag=.false.
    kchoose_start = 0
    kchoose_end = 0
    bot_band = 0
    top_band = 0
    call get_command(cmd)
    write(*,*) 'Current command : ', trim(cmd) 
    narg = command_argument_count()
    write(*,*) 'Argument count : ', narg 

    iarg = 1
    do while (.true.)
        call get_command_argument(iarg, arg, lens, stat)
        if (len_trim(arg) == 0) exit 
        if (trim(arg) == '-nk') then
            kchoose_flag = .true.
            iarg = iarg + 1
            call get_command_argument(iarg, arg, lens, stat)
            read(arg, *) kchoose_start
            iarg = iarg + 1
            call get_command_argument(iarg, arg, lens, stat)
            read(arg, *) kchoose_end
        endif
        if (trim(arg) == '-nb') then 
            iarg = iarg + 1
            call get_command_argument(iarg, arg, lens, stat)
            read(arg, *) bot_band
            iarg = iarg + 1
            call get_command_argument(iarg, arg, lens, stat)
            read(arg, *) top_band
        endif 

        iarg = iarg + 1
    enddo 
    !
    allocate(rot_input(3,3,max_nsym))  ;  rot_input=0
    allocate(tau_input(3,max_nsym))     ;  tau_input=0.0_dp
    allocate(SU2_input(2,2,max_nsym)) ; SU2_input=cmplx(0.0_dp,0.0_dp,kind=dp)
    allocate(time_reversal_input(max_nsym)) ; time_reversal_input=0
    allocate(spin_rot_input(3,3,max_nsym)) ; spin_rot_input=0.0_dp
    !
    ssg_num = ''
    !
    call get_ssg_from_identifySSG(ssg_num,num_sym,rot_input,tau_input,SU2_input,spin_rot_input,time_reversal_input)
    !
    call read_outcar() 
    !
    call output_ssg_operator(ssg_num,num_sym,rot_input,tau_input,SU2_input,spin_rot_input,time_reversal_input)
    !
    call setarray()
    !
    allocate(rot(3,3,num_sym))                      ; rot=0
    allocate(SO3(3,3,num_sym))                      ; SO3=0.d0
    allocate(SU2(2,2,num_sym))                      ; SU2=0.d0 
    allocate(tau(3,num_sym))                      ; tau=0.d0 
    allocate(kphase(num_sym))                       ; kphase=0.d0
    allocate(tilte_vec(max_plane,num_sym))          ; tilte_vec=0
    allocate(Gphase(max_plane,num_sym))             ; gphase=0.d0 
    allocate(litt_group(num_sym))                   ; litt_group=0        
    allocate(time_reversal(num_sym))                ; time_reversal=0  
    allocate(SO3_unitary(3,3,num_sym))              ; SO3_unitary=0.d0
    allocate(SU2_unitary(2,2,num_sym))              ; SU2_unitary=0.d0
    allocate(rot_unitary(3,3,num_sym))         ; rot_unitary=0
    allocate(tau_unitary(3,num_sym))                ; tau_unitary=0.d0
    allocate(litt_group_unitary(num_sym))            ; litt_group_unitary=0   
    allocate(spin_rot(3,3,num_sym))                 ; spin_rot=0.0_dp
    !
    if(.not. kchoose_flag) then
        kchoose_start = 1
        kchoose_end = num_k
    endif
    !

    
    if(kchoose_end > num_k) then
        stop  'kpoints chosen is larger than the number of kpoints!!!'
    endif

    do kkk = kchoose_start, kchoose_end
        
        call read_wavecar(kkk)
        
        call kgroup(num_sym, num_sym, rot_input, time_reversal_input, WK, litt_group, num_litt_group)

        num_litt_group_unitary = 0
        do i=1, num_litt_group
            rot(:,:,i) = rot_input(:,:,litt_group(i))
            SO3(:,:,i) = matmul(matmul(br2, rot(:,:,i)), br4)
            SU2(:,:,i) = SU2_input(:,:,litt_group(i))
            spin_rot(:,:,i) = spin_rot_input(:,:,litt_group(i))
            time_reversal(i) = time_reversal_input(litt_group(i))
            tau(:,i) = tau_input(:,litt_group(i))

            if (time_reversal(i)==1) then
                num_litt_group_unitary = num_litt_group_unitary + 1
                litt_group_unitary(num_litt_group_unitary) = litt_group(i)
                SO3_unitary(:,:,num_litt_group_unitary) = SO3(:,:,i)
                SU2_unitary(:,:,num_litt_group_unitary) = SU2(:,:,i)
                rot_unitary(:,:,num_litt_group_unitary) = rot(:,:,i)
                tau_unitary(:,num_litt_group_unitary) = tau(:,i)
            endif
            
        enddo


        if (nspin==2) then
            call judge_up_down_relation(num_litt_group,SU2,time_reversal,spin_no_reversal)
            if (.not. spin_no_reversal) then
                call read_wavecar_spin_polarized(kkk)
            endif
        endif
        
        write(*,'(A)')'********************************************************************************'
        write(*,*)
        write(*,*)

        call get_k_name( WK ,k_name, k_frac_symbol)


        if (nspin==2) then
            if (spin_no_reversal) then
                write(*,'(A,1I3,A)')'knum = ',kkk,' spin = up'
            else
                write(*,'(A)')'There is a SSG operator flipping spin in the k-little group.'
                write(*,'(A,1I3,A)')'knum = ',kkk,' spin = up & down'
            endif
        else
            write(*,'(A,1I3)')'knum = ',kkk
        endif

        write(*,'(A,3F9.6)')'K = ',WK
        write(*,'(A)')'kname = '//trim(adjustl(k_name))//'    Fractional coordinate: '//trim(adjustl(k_frac_symbol))//' (given in the conventional basis)'
       
        call pw_setup_ssg(WK, num_litt_group_unitary, &
                    max_plane, ncnt, igall, &
                    rot_unitary, SO3_unitary,tau_unitary,&
                    kphase, Gphase, tilte_vec)
                    
        allocate(op_order(num_litt_group))
        allocate(ch_table(num_litt_group,num_litt_group))
        allocate(ch_unitary_table(num_litt_group,num_litt_group))
        allocate(discriminant_value(num_litt_group))
        allocate(torsion(num_litt_group))
        allocate(phase(num_litt_group))


        
        call get_ch_from_op(num_litt_group, spin_rot(:,:,1:num_litt_group), rot(:,:,1:num_litt_group), &
                            tau(:,1:num_litt_group), SU2(:,:,1:num_litt_group), time_reversal(1:num_litt_group), &
                            WK, op_order, irrep_num, ch_table, phase, &
                            irrep_unitary_num, ch_unitary_table, torsion)

        allocate(ch_table_less(irrep_num,num_litt_group_unitary))
        allocate(ch_unitary_table_less(irrep_unitary_num,num_litt_group_unitary))
        allocate(irrep_coirrep_relation(2,irrep_num))
        allocate(irrep_name_list(irrep_num))


        ch_table_less(1:irrep_num,1:num_litt_group_unitary) = ch_table(1:irrep_num,1:num_litt_group_unitary)
        ch_unitary_table_less(1:irrep_unitary_num,1:num_litt_group_unitary) = ch_unitary_table(1:irrep_unitary_num,1:num_litt_group_unitary)

        deallocate(ch_table)
        deallocate(ch_unitary_table)
        
        

        call find_relation_between_unitary_irrep_coirrep(num_litt_group_unitary,irrep_num,ch_table_less,irrep_unitary_num,ch_unitary_table_less,irrep_coirrep_relation,&
                                                        discriminant_value,torsion)

        call output_character_table(k_name,num_litt_group,num_litt_group_unitary,litt_group,op_order,irrep_num,ch_table_less,phase, &
                                irrep_unitary_num,ch_unitary_table_less,irrep_coirrep_relation,irrep_name_list,discriminant_value)


        call get_comprel(num_litt_group,num_litt_group_unitary,litt_group,op_order,irrep_num,irrep_name_list,ch_table_less)

        do i=1,irrep_num
            do j=1,num_litt_group_unitary
                ch_table_less(i,j) = ch_table_less(i,j) * phase(j)
            enddo
        enddo

        if (nspin==1 .or. spin_no_reversal) then
            call irrep_ssg( num_litt_group_unitary,litt_group_unitary,&
                            rot_unitary, tau_unitary, SO3_unitary, SU2_unitary, &
                            kkk, WK, kphase, &
                            num_bands, bot_band, top_band, EE, &
                            max_plane, ncnt, &
                            coeffa, coeffb, &
                            irrep_num, ch_table_less, &
                            irrep_name_list, &
                            G_phase_pw=Gphase, rot_vec_pw=tilte_vec)
        else
            call irrep_ssg( num_litt_group_unitary,litt_group_unitary,&
                    rot_unitary, tau_unitary, SO3_unitary, SU2_unitary, &
                    kkk, WK, kphase, &
                    num_bands*2, bot_band*2-1, top_band*2, EE, &
                    max_plane, ncnt, &
                    coeffa, coeffb, &
                    irrep_num, ch_table_less, &
                    irrep_name_list, &
                    G_phase_pw=Gphase, rot_vec_pw=tilte_vec)
        endif

        deallocate(ch_table_less)
        deallocate(ch_unitary_table_less)
        deallocate(op_order)
        deallocate(irrep_coirrep_relation)
        deallocate(irrep_name_list)
        deallocate(discriminant_value)
        deallocate(torsion)
        deallocate(phase)

    enddo 

    call end_get_comprel()

    if (nspin==2) then
    do kkk = kchoose_start+num_k, kchoose_end+num_k

        call read_wavecar(kkk)
        
        call kgroup(num_sym, num_sym, rot_input, time_reversal_input, WK, litt_group, num_litt_group)

        num_litt_group_unitary = 0
        do i=1, num_litt_group
            rot(:,:,i) = rot_input(:,:,litt_group(i))
            SO3(:,:,i) = matmul(matmul(br2, rot(:,:,i)), br4)
            SU2(:,:,i) = SU2_input(:,:,litt_group(i))
            spin_rot(:,:,i) = spin_rot_input(:,:,litt_group(i))
            time_reversal(i) = time_reversal_input(litt_group(i))
            tau(:,i) = tau_input(:,litt_group(i))

            if (time_reversal(i)==1) then
                num_litt_group_unitary = num_litt_group_unitary + 1
                litt_group_unitary(num_litt_group_unitary) = litt_group(i)
                SO3_unitary(:,:,num_litt_group_unitary) = SO3(:,:,i)
                SU2_unitary(:,:,num_litt_group_unitary) = SU2(:,:,i)
                rot_unitary(:,:,num_litt_group_unitary) = rot(:,:,i)
                tau_unitary(:,num_litt_group_unitary) = tau(:,i)
            endif
            
        enddo

        call judge_up_down_relation(num_litt_group,SU2,time_reversal,spin_no_reversal)
        if (.not. spin_no_reversal) then
            call read_wavecar_spin_polarized(kkk-num_k)
        endif

        write(*,'(A)')'********************************************************************************'
        write(*,*)
        write(*,*)

        call get_k_name( WK ,k_name, k_frac_symbol)
        
        if (spin_no_reversal) then
            write(*,'(A,1I3,A)')'knum = ',kkk-num_k,' spin = down'
        else
            write(*,'(A)')'There is a SSG operator flipping spin in the k-little group.'
            write(*,'(A,1I3,A)')'knum = ',kkk-num_k,' spin = up & down'
        endif

        write(*,'(A,3F9.6,A)')'K = ',WK,' kname = '//trim(adjustl(k_name))
        
        call pw_setup_ssg(WK, num_litt_group_unitary, &
            max_plane, ncnt, igall, &
            rot_unitary, SO3_unitary,tau_unitary,&
            kphase, Gphase, tilte_vec)
                    
        allocate(op_order(num_litt_group))
        allocate(ch_table(num_litt_group,num_litt_group))
        allocate(ch_unitary_table(num_litt_group,num_litt_group))
        allocate(discriminant_value(num_litt_group))
        allocate(torsion(num_litt_group))
        allocate(phase(num_litt_group))


        
        call get_ch_from_op(num_litt_group, spin_rot(:,:,1:num_litt_group), rot(:,:,1:num_litt_group), &
                            tau(:,1:num_litt_group), SU2(:,:,1:num_litt_group), time_reversal(1:num_litt_group), &
                            WK, op_order, irrep_num, ch_table, phase, irrep_unitary_num, ch_unitary_table, torsion)

        allocate(ch_table_less(irrep_num,num_litt_group_unitary))
        allocate(ch_unitary_table_less(irrep_unitary_num,num_litt_group_unitary))
        allocate(irrep_coirrep_relation(2,irrep_num))
        allocate(irrep_name_list(irrep_num))

        ch_table_less(1:irrep_num,1:num_litt_group_unitary) = ch_table(1:irrep_num,1:num_litt_group_unitary)
        ch_unitary_table_less(1:irrep_unitary_num,1:num_litt_group_unitary) = ch_unitary_table(1:irrep_unitary_num,1:num_litt_group_unitary)

        deallocate(ch_table)
        deallocate(ch_unitary_table)



        call find_relation_between_unitary_irrep_coirrep(num_litt_group_unitary,irrep_num,ch_table_less,irrep_unitary_num,ch_unitary_table_less,irrep_coirrep_relation,&
                                                        discriminant_value,torsion)

        call output_character_table(k_name,num_litt_group,num_litt_group_unitary,litt_group,op_order,irrep_num,ch_table_less,phase,&
                                irrep_unitary_num,ch_unitary_table_less,irrep_coirrep_relation,irrep_name_list,discriminant_value)

        call get_comprel(num_litt_group,num_litt_group_unitary,litt_group,op_order,irrep_num,irrep_name_list,ch_table_less)

        do i=1,irrep_num
            do j=1,num_litt_group_unitary
                ch_table_less(i,j) = ch_table_less(i,j) * phase(j)
            enddo
        enddo

        call irrep_ssg( num_litt_group_unitary,litt_group_unitary,&
                        rot_unitary, tau_unitary, SO3_unitary, SU2_unitary, &
                        kkk, WK, kphase, &
                        num_bands, bot_band, top_band, EE, &
                        max_plane, ncnt, &
                        coeffa, coeffb, &
                        irrep_num, ch_table_less, &
                        irrep_name_list, &
                        G_phase_pw=Gphase, rot_vec_pw=tilte_vec)


        deallocate(ch_table_less)
        deallocate(ch_unitary_table_less)
        deallocate(op_order)
        deallocate(irrep_coirrep_relation)
        deallocate(irrep_name_list)
        deallocate(discriminant_value)
        deallocate(torsion)
        deallocate(phase)
    enddo 
    endif

    call downarray()
    call end_get_comprel()
    deallocate(rot)
    deallocate(SO3)
    deallocate(SU2)
    deallocate(tau)
    deallocate(kphase)
    deallocate(tilte_vec)
    deallocate(Gphase)
    deallocate(litt_group)
    deallocate(time_reversal)
    deallocate(rot_unitary)
    deallocate(SO3_unitary)
    deallocate(SU2_unitary)
    deallocate(litt_group_unitary)
    deallocate(tau_unitary)
    deallocate(spin_rot)
    WRITE(6,*) 
    WRITE(6,*) "*****************************************************"
    WRITE(6,*) 
    WRITE(6,*) "TOTAL END"


end program irvsp 

