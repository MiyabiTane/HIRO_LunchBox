#!/usr/bin/env roseus

(ros::roseus "init")

(ros::load-ros-package "jsk_recognition_msgs")
(setq *camera-frame* "head_camera_rgb_optical_frame")
(setq *pub-topic* "/xyz_to_screenpoint/input")
(ros::advertise *pub-topic* geometry_msgs::PointStamped 1)
(setq *sub-topic* "/xyz_to_screenpoint/output") 
(ros::rate 1)

;;init
(setq pub_msg (instance geometry_msgs::PointStamped :init))

;;use tf
(unless (boundp '*tfl*)
  (setq *tfl* (instance ros::transform-listener :init)))

;;use xyz_to_screenpoint
(defun set_pubmsg (x y z)
  (setq coords (make-coords :pos (float-vector x y z)))
  ;;(setq pub-coords (send (send *tfl* :lookup-transform *camera-frame* "WAIST" (ros::time 0))
  ;;:transform coords))
  (setq pub-coords (send (send *tfl* :lookup-transform *camera-frame* "WAIST" (ros::time 0))
  			 :transform coords))
  (setq pub-pos (send pub-coords :pos))
  (send (send pub_msg :point) :x (elt pub-pos 0))
  (send (send pub_msg :point) :y (elt pub-pos 1))
  (send (send pub_msg :point) :z (elt pub-pos 2))
  )

(defun cb (msg)
  (setq 2D_x (send (send msg :point) :x))
  (setq 2D_y (send (send msg :point) :y))
  (format t "x: ~A, y: ~A~%" 2D_x 2D_y)
  (setq catch-flag t)
  )

(defun get_2D_pos (x y z)
  (set_pubmsg x y z)
  (setq catch-flag nil)
  (ros::subscribe *sub-topic* geometry_msgs::PointStamped #'cb)
  (until catch-flag
	 (ros::publish *pub-topic* pub_msg)
	 (ros::spin-once)
	 (ros::sleep))
  (ros::unsubscribe *sub-topic*)
  )

(defun main ()
  (get_2D_pos 464.363 51.7383 -50.5315)
  (get_2D_pos 354.562 151.793 -50.5315)
  )

(main)
  
  
  
