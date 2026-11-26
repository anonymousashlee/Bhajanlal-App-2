import * as THREE from 'three';
import { rand, clamp, dampAngle } from './utils.js';

const M = (c, o = {}) => new THREE.MeshStandardMaterial({ color: c, roughness: 0.6, metalness: 0.3, ...o });

export class Vehicle {
  constructor(scene, opts = {}) {
    this.scene = scene;
    this.pos = new THREE.Vector3(opts.x || 0, 0, opts.z || 0);
    this.vel = new THREE.Vector3();
    this.speed = 0;
    this.heading = opts.heading || 0;
    this.steer = 0;
    this.maxSpeed = 42;
    this.health = 100;
    this.dead = false;
    this.occupied = !!opts.occupied;
    this.stolenByPlayer = !!opts.stolenByPlayer;
    this.ai = null;
    this.game = null;

    this.group = new THREE.Group();
    this.group.position.copy(this.pos);
    this.group.rotation.y = this.heading;

    // body
    const color = opts.color || 0xff2e88;
    const body = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.9, 4.6), M(color));
    body.position.y = 0.6;
    body.castShadow = true;
    this.group.add(body);
    this.model = { body, under: body, L: 4.6 };
    // wheels
    for (const [sx, sz] of [[-1.1, 1.6], [1.1, 1.6], [-1.1, -1.6], [1.1, -1.6]]) {
      const w = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 0.3, 12), M(0x1a1a1a));
      w.rotation.z = Math.PI / 2;
      w.position.set(sx, 0.35, sz);
      this.group.add(w);
    }
    // headlights
    const hl = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.2, 0.1), new THREE.MeshBasicMaterial({ color: 0xfff6d8 }));
    hl.position.set(-0.7, 0.6, 2.35); this.group.add(hl);
    const hr = hl.clone(); hr.position.x = 0.7; this.group.add(hr);

    scene.add(this.group);
  }

  update(dt, input, world, vfx) {
    if (this.dead) {
      if (vfx) vfx.tireSmoke(this.pos, 0.6);
      return;
    }
    const throttle = input.throttle || 0;
    const brake = input.brake || 0;
    const steer = input.steer || 0;
    const handbrake = !!input.handbrake;

    // steering
    this.steer = dampAngle ? steer : steer;
    const steerAmt = steer * 0.6;
    this.steer = this.steer * 0.8 + steerAmt * 0.2;

    // acceleration
    if (throttle > 0) this.speed += 30 * dt * (1 - this.speed / this.maxSpeed);
    if (brake > 0) this.speed -= 22 * dt;
    if (handbrake) this.speed *= 0.92;
    // friction
    this.speed *= (1 - 0.5 * dt);
    this.speed = clamp(this.speed, -8, this.maxSpeed);

    // turn
    if (Math.abs(this.speed) > 0.5) {
      this.heading += this.steer * (this.speed > 0 ? 1 : -1) * Math.min(1, Math.abs(this.speed) / 10) * dt * 2.2;
    }

    // move
    this.pos.x += Math.sin(this.heading) * this.speed * dt;
    this.pos.z += Math.cos(this.heading) * this.speed * dt;
    this.pos.y = 0;
    this.vel.set(Math.sin(this.heading) * this.speed, 0, Math.cos(this.heading) * this.speed);

    // collisions with buildings
    if (world && world.resolve) {
      const before = { x: this.pos.x, z: this.pos.z };
      world.resolve(this.pos, 1.2);
      if (Math.abs(this.pos.x - before.x) > 0.01 || Math.abs(this.pos.z - before.z) > 0.01) {
        const impact = Math.abs(this.speed);
        this.speed *= 0.4;
        if (this.game && this.game.onCrash) this.game.onCrash(impact, this);
        if (vfx) vfx.sparks(new THREE.Vector3(this.pos.x, 0.7, this.pos.z), 8);
      }
    }

    // bounds
    const half = 320;
    if (Math.abs(this.pos.x) > half - 2) { this.pos.x = Math.sign(this.pos.x) * (half - 2); this.speed *= -0.3; }
    if (Math.abs(this.pos.z) > half - 2) { this.pos.z = Math.sign(this.pos.z) * (half - 2); this.speed *= -0.3; }

    // health/damage from crashes
    if (Math.abs(this.speed) > 30 && Math.random() < 0.01) {
      this.health -= 1;
      if (this.health <= 0) {
        this.dead = true;
        if (this.game && this.game.onVehicleExplode) this.game.onVehicleExplode();
      }
    }

    // exhaust
    if (vfx && Math.abs(this.speed) > 2) {
      const dir = { x: Math.sin(this.heading), z: Math.cos(this.heading) };
      vfx.exhaust(new THREE.Vector3(this.pos.x - dir.x * 2.3, 0.4, this.pos.z - dir.z * 2.3), dir);
    }
    // tire smoke when handbrake
    if (vfx && handbrake && Math.abs(this.speed) > 5) {
      vfx.tireSmoke(this.pos, 1.2);
    }

    this.group.position.copy(this.pos);
    this.group.rotation.y = this.heading;
  }

  applyDamage(n) {
    this.health -= n;
    if (this.health <= 0 && !this.dead) {
      this.dead = true;
      if (this.game && this.game.onVehicleExplode) this.game.onVehicleExplode();
    }
  }
}