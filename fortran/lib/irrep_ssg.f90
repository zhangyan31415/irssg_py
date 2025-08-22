! irssg
! shengzhang221@mails.ucas.ac.cn

subroutine irrep_ssg(num_litt_group_unitary, litt_group_unitary, rot, tau,&
                      SO3, SU2, &
                      KKK, WK, kphase, &
                      num_bands, m, n, ene_bands, &
                      dim_basis, num_basis, &
                      coeffa, coeffb, irrep_num, ch_table, &
                      irrep_name_list, &
                      G_phase_pw, rot_vec_pw)

    use lib_comms
    use chrct
    implicit none 
    intrinsic :: nint

    ! number of space-group operations (module the integer lattice translations) 
    ! should not be changed for different k
    integer,     intent(in) :: num_litt_group_unitary
    integer,     intent(in) :: litt_group_unitary(num_litt_group_unitary)

    ! the rotation part of space-group operations with respect to primitive lattice vectors
    ! should not be changed for different k
    integer,     intent(in) :: rot(3,3,num_litt_group_unitary)

    ! the translation part of space-group operations with respect to primitive lattice vectors
    ! should not be changed for different k
    real(dp),    intent(in) :: tau(3,num_litt_group_unitary)

    ! the rotation part of space-group operations given in Cartesian coordinates
    ! should not be changed for different k
    real(dp),    intent(in) :: SO3(3,3,num_litt_group_unitary)

    ! the rotation part of space-group operations given in spin-1/2 space
    ! should not be changed for different k
    complex(dp), intent(in) :: SU2(2,2,num_litt_group_unitary)
    complex(dp) :: SU2_(2,2,num_litt_group_unitary)

    ! the sequential number of the given k-point
    integer,     intent(in) :: KKK

    ! the coordinate of the k-point with respect to primitive reciprocal lattice vectors
    real(dp),    intent(in) :: WK(3)

    ! the k-dependent phase factors due to the translation part of space-group operations
    complex(dp), intent(in) :: kphase(num_litt_group_unitary)

    ! the total number of bands
    integer,     intent(in) :: num_bands

    ! the IRs of the set of bands [m,n] are computed
    integer,     intent(in) :: m, n 

    ! the energy of bands at the k-point
    real(dp),    intent(in) :: ene_bands(num_bands) 

    ! the reserved number of the PW/TB basis
    ! if rot_vec_pw is given, dim_basis should be larger than the PW number of any k-points
    ! if rot_mat_tb is given, one should set dim_basis = num_basis
    integer,     intent(in) :: dim_basis

    ! the number of PW or orthogonal TB basis for the k-point 
    ! (note: the PW basis numbers for different k-points are usually different)
    integer,     intent(in) :: num_basis  

    ! the coefficient of spinor up part of wave functions at the given k-point 
    ! (note: coeffup_basis(1:num_basis,1:num_bands) is nonzero)
    complex(dp), intent(in) :: coeffa(dim_basis, num_bands)

    ! the coefficent of spinor down part of wave functions at the given k-point if spinor is .true.
    ! (note: coeffdn_basis(1:num_basis,1:num_bands) is nonzero)
    complex(dp), intent(in) :: coeffb(dim_basis, num_bands)
 
    ! the phase factor dependent by the PW vectors
    complex(dp), intent(in), optional :: G_phase_pw(dim_basis, num_litt_group_unitary)

    ! the transformation vectors of space-group operations, which send the jth PW to the j'th PW
    integer,     intent(in), optional :: rot_vec_pw(dim_basis, num_litt_group_unitary)

    integer, intent(in) :: irrep_num

    complex(dp), intent(in) :: ch_table(irrep_num,num_litt_group_unitary)

    character(len=15), intent(in) :: irrep_name_list(irrep_num)


    ! reordered symmetry operations according to Bilbao
    integer                  :: invrot(3,3,MAXSYM)

    ! little group of bilbao k
    integer                  :: littg_bilbao(MAXSYM)
    integer                  :: num_littg_bilbao

    integer                 :: littg_input(MAXSYM)


    ! calculated character tables, without outer k phase
    complex(dp)              :: chrct_set(num_bands, MAXSYM)

    ! degenerate informations of input bands
    integer                  :: deg_set(num_bands)
    integer                  :: numdeg_set(num_bands)

    ! representation names
    character(len=20)        :: reps_set(num_bands)
    integer                  :: numreps_set(num_bands)

    integer  :: i, j

    if (.not. allocated(save_chrct)) then
        save_kcount = 0
        allocate(save_chrct(num_bands, MAXKSAVE))
        allocate(save_numdeg(num_bands, MAXKSAVE))
        allocate(save_numrep(num_bands, MAXKSAVE))
        allocate(save_ktype(MAXKSAVE))
        save_chrct = -7
        save_numdeg = 0
        save_numrep = 0
        save_ktype = 0
    endif

    ! do i = 1, num_litt_group_unitary
    !     call invmati(rot(:,:,i), invrot(:,:,i))
    ! enddo

    save_kcount = save_kcount + 1
    ! write(*,*) SU2,coeffa,coeffb,ene_bands,G_phase_pw,rot_vec_pw,chrct_set

    call irssg_chrct(num_litt_group_unitary, SU2, &
                        num_litt_group_unitary, &
                        num_bands, m, n, ene_bands, &
                        dim_basis, num_basis, &
                        coeffa, coeffb, &
                        chrct_set, deg_set, numdeg_set, &
                        map_vec=rot_vec_pw, G_phase_pw=G_phase_pw) 
    
    call irssg_reps(num_litt_group_unitary,litt_group_unitary,num_bands,m, n, ene_bands,&
                            irrep_num, ch_table, irrep_name_list, &
                            chrct_set, deg_set, numdeg_set, kphase, numreps_set)

end subroutine irrep_ssg


subroutine pw_setup_ssg(WK, num_litt_group_unitary,&
                    dim_basis, num_basis, Gvec, &
                    rot_unitary, SO3_unitary, tau_unitary, &
                    kphase, Gphase_pw, rot_vec_pw)

    use lib_comms
    implicit none 

    ! the coordinates of the k-point with respect to primitive reciprocal lattice vectors
    real(dp),    intent(in)  :: WK(3)

    ! the number of space-group operations 
    integer,     intent(in)  :: num_litt_group_unitary
    
    ! the translation part of space-group operations with respect to primitive lattice vectors
    real(dp),    intent(in) :: tau_unitary(3,num_litt_group_unitary)

    ! the reserved number of the PW_basis (dim_basis >= num_basis)
    integer,     intent(in)  :: dim_basis 

    ! the number of PW for the k-point (note: num_basis for different k-points are usually different)
    integer,     intent(in)  :: num_basis 

    ! the plane-wave G-vector with respected to reciprocal lattice vectors
    integer,     intent(in)  :: Gvec(3, dim_basis)

    ! the rotation part of space-group operations with respect to primitive lattice vectors
    integer,     intent(in) :: rot_unitary(3,3,num_litt_group_unitary)

    ! the rotation part of space-group operations in Cartesian coordinates
    real(dp),    intent(in) :: SO3_unitary(3,3,num_litt_group_unitary)


    ! the k-dependent phase factors due to the translation part of space-group operations
    complex(dp), intent(out) :: kphase(num_litt_group_unitary)

    ! the phase factor dependent by the PW vectors
    complex(dp), intent(out) :: Gphase_pw(dim_basis, num_litt_group_unitary)

    ! the transformation vectors of Rs, which send the jth PW to the j'th PW
    integer,     intent(out) :: rot_vec_pw(dim_basis, num_litt_group_unitary)




    ! parameter used inside the library 
    integer :: i, j, irot

    
    complex(dp) :: so3tmp(3,3), su2tmp(2,2)


    integer  :: ind, ikv 
    real(dp) :: RWK(3), RKV(3)
    real(dp) :: diff, ang
    real(dp) :: KV(3,dim_basis)

    integer  :: invrot(3,3,num_litt_group_unitary)

    real(dp) :: A(3,3)

    do irot = 1, num_litt_group_unitary
        call invmati(rot_unitary(:,:,irot), invrot(:,:,irot)) 
    enddo 
    
    ! get kphase
    kphase = 0.d0 
    do irot = 1, num_litt_group_unitary
        ang = -2.d0*PI*( WK(1)*tau_unitary(1,irot) &
                          +WK(2)*tau_unitary(2,irot) &
                          +WK(3)*tau_unitary(3,irot))
        kphase(irot) = cmplx(dcos(ang), dsin(ang))
    enddo 
    
    ! get Gphase and rot_vec_pw
    KV = 0.d0 
    do ikv = 1, num_basis 
        KV(:,ikv) = dble(Gvec(:,ikv)) + WK(:)
    enddo 


    Gphase_pw = 0.d0
    rot_vec_pw = 0
    do irot = 1, num_litt_group_unitary
        do ikv = 1, num_basis 
            
            do j = 1, 3
                RKV(j) = KV(1,ikv)*dble(invrot(1,j,irot)) &
                        +KV(2,ikv)*dble(invrot(2,j,irot)) &
                        +KV(3,ikv)*dble(invrot(3,j,irot))

            enddo 

            ind = 1
            do while ( (abs(RKV(1)-KV(1,ind)) &
                       +abs(RKV(2)-KV(2,ind)) &
                       +abs(RKV(3)-KV(3,ind))) > 1.d-3 .and. (ind <= num_basis) )
                ind = ind + 1
            enddo 

            if (ind == num_basis + 1) then 
                write(6,*) "cannot find (k+G)inv(Ri)"
                stop
            endif 

            ang = 0.d0 
            do j = 1, 3
                ang = ang - 2.d0*PI*tau_unitary(j, irot)*(KV(j,ind)-WK(j))!!!!
            enddo 

            Gphase_pw(ikv, irot)  = cmplx(dcos(ang), dsin(ang))
            rot_vec_pw(ikv, irot) = ind 

        enddo 
    enddo     


end subroutine pw_setup_ssg


subroutine kgroup(dim_sym, num_sym, rot, time_reversal, veck, litt_group, num_litt_group)

    !!! This subroutine find the little group G(k) of wave vector k
    !!! \hat{R}\vec{k} = \vec{k} + \vec{Km}
    !!! Note that \hat{R}\vec{k} = (k1,k2,k3)Z^{-1}(g1,g2,g3)^T
    !!! Thus the input rotation matrix is inv(Ri)

    use lib_comms
    implicit none 

    integer, intent(in)  :: dim_sym, num_sym 
    integer, intent(in)  :: rot(3,3,dim_sym)
    real(dp), intent(in)  :: veck(3)

    integer, intent(out) :: litt_group(dim_sym)
    integer, intent(out) :: num_litt_group 

    integer :: i, j
    real(dp) :: Rveck(3), diff 
    real(dp), parameter   :: tolk = 0.1E-4 
    integer,intent(in) :: time_reversal(dim_sym)
    integer :: invrot(3,3)

    

    litt_group = 0
    num_litt_group = 0
    do i = 1, num_sym 
        call invmati(rot(:,:,i), invrot)
        if (time_reversal(i) == 1) then
            do j = 1, 3
                Rveck(j) = dot_product(veck(:),invrot(:,j))-veck(j)
            enddo 
        else
            do j = 1, 3
                Rveck(j) = -dot_product(veck(:),invrot(:,j))-veck(j)
            enddo 
        endif

        diff = dabs(nint(Rveck(1))-Rveck(1)) &
              +dabs(nint(Rveck(2))-Rveck(2)) &
              +dabs(nint(Rveck(3))-Rveck(3))  
        if (diff <= tolk) then 
            num_litt_group = num_litt_group + 1
            litt_group(num_litt_group) = i
        endif 
    enddo 
    return 

end subroutine kgroup 


subroutine get_k_name(kpoints, kname, k_frac_symbol)

    use bilbao
    implicit none
    real(dp), intent(in) :: kpoints(3)
    character(len=4), intent(out) :: kname
    ! character(len=15), intent(out) :: kpath_name
    character(len=15), intent(out) :: k_frac_symbol
    real(dp) :: k_tmp(3)
    k_tmp = kpoints
    kname = ''
    k_frac_symbol = ''
    call bilbao_getkid(k_tmp, kname, k_frac_symbol)

end subroutine get_k_name

subroutine load_bilbao(sgn)

    use bilbao
    implicit none
    integer, intent(in) :: sgn
    call bilbao_read(sgn)
end subroutine load_bilbao